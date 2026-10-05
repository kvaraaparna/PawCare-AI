"""
PawCare AI – Explainable AI (Grad-CAM) Module
=============================================
Computes Gradient-weighted Class Activation Mapping (Grad-CAM) for ResNet-18.
Highlights visual regions in the input image that contributed most strongly
to the model's predicted disease classification.

Target Layer: model.layer4[-1] (Final convolutional block before classifier).
"""

from __future__ import annotations

import base64
import contextlib
import io
import logging
from typing import Any, cast

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torch import nn
from torchvision import transforms

logger = logging.getLogger("PawCareAI.GradCAM")

# Preprocessing transform matching ResNet18 input pipeline
gradcam_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def apply_jet_colormap(cam: np.ndarray) -> np.ndarray:
    """
    Applies a standard Jet colormap (Blue -> Cyan -> Green -> Yellow -> Red)
    to a 2D float array in range [0, 1].
    Implemented in pure NumPy for high performance and zero external dependencies.
    """
    cam = np.clip(cam, 0.0, 1.0)
    r = np.clip(1.5 - np.abs(4.0 * cam - 3.0), 0.0, 1.0)
    g = np.clip(1.5 - np.abs(4.0 * cam - 2.0), 0.0, 1.0)
    b = np.clip(1.5 - np.abs(4.0 * cam - 1.0), 0.0, 1.0)
    rgb = np.stack([r, g, b], axis=-1)
    return (rgb * 255.0).astype(np.uint8)


def pil_to_base64(img: Image.Image, format: str = "JPEG", quality: int = 90) -> str:
    """Encodes a PIL Image into a base64 data URL string."""
    buffer = io.BytesIO()
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(buffer, format=format, quality=quality)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{encoded}"


def generate_gradcam(
    model: nn.Module,
    pil_image: Image.Image,
    target_class: int,
    device: torch.device | None = None,
    alpha: float = 0.55
) -> dict[str, Any] | None:
    """
    Generates a Grad-CAM explanation heatmap overlay for the specified class.

    Args:
        model: ResNet-18 PyTorch model in eval mode.
        pil_image: Original PIL Image uploaded by the user.
        target_class: Target class index (0 to 3).
        device: Torch device (CPU or CUDA).
        alpha: Blending weight for original image vs heatmap (0.55 original, 0.45 heatmap).

    Returns:
        Dict containing:
          - "overlay_pil": Blended PIL Image
          - "overlay_base64": Base64 data URL for frontend rendering
          - "heatmap_raw": 2D normalized numpy array
          - "target_class": Target class index evaluated
        Or None if an error occurs.
    """
    if model is None or pil_image is None:
        logger.warning("Grad-CAM invoked with missing model or image.")
        return None

    if device is None:
        device = next(model.parameters()).device

    # ResNet-18 final convolutional block in layer4
    try:
        target_layer = model.layer4[-1]
    except (AttributeError, IndexError) as e:
        logger.error(f"Cannot locate target layer model.layer4[-1]: {e}")
        return None

    activations = []
    gradients = []

    def forward_hook(module, input, output):
        activations.append(output)

    def backward_hook(module, grad_input, grad_output):
        if grad_output and len(grad_output) > 0 and grad_output[0] is not None:
            gradients.append(grad_output[0])

    forward_handle = None
    backward_handle = None

    try:
        # Register PyTorch hooks on target layer
        forward_handle = target_layer.register_forward_hook(forward_hook)
        backward_handle = target_layer.register_full_backward_hook(backward_hook)

        # Prepare input tensor with gradients enabled
        orig_w, orig_h = pil_image.size
        input_tensor = cast(torch.Tensor, gradcam_transform(pil_image.convert("RGB"))).unsqueeze(0).to(device)
        input_tensor.requires_grad_(True)

        model.eval()

        # Run forward pass inside gradient context
        with torch.enable_grad():
            model.zero_grad()
            logits = model(input_tensor)

            if target_class < 0 or target_class >= logits.shape[1]:
                target_class = int(torch.argmax(logits, dim=1).item())

            target_score = logits[0, target_class]
            target_score.backward()

        if not activations or not gradients:
            logger.error("Failed to capture activations or gradients during Grad-CAM backprop.")
            return None

        # Extract captured feature map activations and backpropagated gradients
        act = activations[0].detach()  # Shape: [1, 512, 7, 7]
        grad = gradients[0].detach()   # Shape: [1, 512, 7, 7]

        # Global average pooling of gradients along spatial dimensions to compute importance weights
        weights = torch.mean(grad, dim=(2, 3), keepdim=True)  # Shape: [1, 512, 1, 1]

        # Weighted linear combination of activation maps
        cam = torch.sum(weights * act, dim=1, keepdim=True)  # Shape: [1, 1, 7, 7]

        # Apply ReLU to focus exclusively on features with positive influence on the target class
        cam = F.relu(cam)

        # Normalize CAM to range [0, 1]
        cam_min = cam.min()
        cam_max = cam.max()
        if cam_max - cam_min > 1e-7:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = torch.zeros_like(cam)

        # Interpolate low-resolution 7x7 heatmap smoothly up to original image resolution
        cam_resized = F.interpolate(
            cam,
            size=(orig_h, orig_w),
            mode="bilinear",
            align_corners=False
        )[0, 0].cpu().numpy()

        cam_norm = np.clip(cam_resized, 0.0, 1.0)

        # Generate RGB heatmap with pure NumPy Jet colormap
        heatmap_rgb = apply_jet_colormap(cam_norm)

        # Convert original PIL image to numpy array in range [0, 255]
        orig_rgb = np.array(pil_image.convert("RGB"), dtype=np.uint8)

        # Blend original image and heatmap overlay with specified alpha
        blended = (orig_rgb.astype(np.float32) * (1.0 - alpha) + heatmap_rgb.astype(np.float32) * alpha)
        blended = np.clip(blended, 0, 255).astype(np.uint8)

        overlay_pil = Image.fromarray(blended)
        overlay_base64 = pil_to_base64(overlay_pil, format="JPEG", quality=88)

        logger.info(f"Grad-CAM successfully generated for class {target_class} (Layer: model.layer4[-1]).")

        return {
            "overlay_pil": overlay_pil,
            "overlay_base64": overlay_base64,
            "heatmap_raw": cam_norm,
            "target_class": target_class
        }

    except Exception:
        logger.exception("Unexpected error during Grad-CAM generation")
        return None

    finally:
        # Guarantee hook removal to prevent any memory leak
        if forward_handle is not None:
            with contextlib.suppress(Exception):
                forward_handle.remove()
        if backward_handle is not None:
            with contextlib.suppress(Exception):
                backward_handle.remove()
