"""
PawCare AI - Dog Skin Disease Detection Model Training Pipeline
===============================================================
Trains a torchvision ResNet-18 model on dog skin disease photographic samples.

Canonical Class Mapping (STRICT):
  0 = Bacterial_dermatosis
  1 = Fungal_infections
  2 = Healthy
  3 = Hypersensitivity_allergic_dermatosis

Checkpoints:
  Saved to models/dog_disease_resnet18_v2.pth.
  NEVER silently overwrites best_dog_disease_resnet18.pth.
"""

from __future__ import annotations

import argparse
import copy
import logging
import os
import time
from collections.abc import Callable
from typing import Any

import torch
from torch import nn, optim
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, models, transforms

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)
logger = logging.getLogger("PawCareAI.Train")

# Exact class list and canonical index order
CLASSES = [
    "Bacterial_dermatosis",
    "Fungal_infections",
    "Healthy",
    "Hypersensitivity_allergic_dermatosis"
]

CLASS_TO_IDX = {cls_name: i for i, cls_name in enumerate(CLASSES)}

# Transforms
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.15, contrast=0.15),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

class CustomClassFolder(datasets.ImageFolder):
    """
    Subclass of ImageFolder to guarantee the canonical class order
    regardless of directory name alphabetical sorting.
    """
    def find_classes(self, directory: str):
        classes = CLASSES
        class_to_idx = CLASS_TO_IDX
        # Verify classes exist in target directory
        existing = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
        for c in classes:
            if c not in existing:
                logger.warning(f"Class folder '{c}' not found directly in {directory}")
        return classes, class_to_idx

def build_model(num_classes: int = 4) -> nn.Module:
    """Builds a ResNet-18 model initialized with ImageNet weights and 4-class head."""
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    return model

def train_dog_disease_model(
    dataset_dir: str,
    epochs: int = 15,
    batch_size: int = 16,
    learning_rate: float = 0.0001,
    output_path: str | None = None,
    progress_callback: Callable[[dict[str, Any]], None] | None = None
) -> dict[str, Any]:
    """
    Executes training on the validated dataset directory.
    Sends progress reports via progress_callback for web UI integration.
    """
    if output_path is None:
        os.makedirs("models", exist_ok=True)
        output_path = os.path.join("models", "dog_disease_resnet18_v2.pth")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Training initialized on device: {device}")

    # Verify directory structure
    subdirs = [d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))]
    target_root = dataset_dir
    # Handle single subfolder packaging (e.g. Dogs/ or dog_skin_dataset/)
    if len(subdirs) == 1 and all(c not in subdirs for c in CLASSES):
        target_root = os.path.join(dataset_dir, subdirs[0])
        logger.info(f"Using nested dataset root: {target_root}")

    # Load complete dataset with transforms
    full_dataset_train = CustomClassFolder(target_root, transform=train_transform)
    full_dataset_val = CustomClassFolder(target_root, transform=val_transform)

    total_samples = len(full_dataset_train)
    logger.info(f"Total dataset samples detected: {total_samples}")
    if total_samples < 8:
        raise ValueError(f"Insufficient samples for training ({total_samples} found).")

    # 80/20 train/validation split
    generator = torch.Generator().manual_seed(42)
    shuffled_indices = torch.randperm(total_samples, generator=generator).tolist()
    split_idx = int(0.8 * total_samples)

    train_indices = shuffled_indices[:split_idx]
    val_indices = shuffled_indices[split_idx:]

    train_data = Subset(full_dataset_train, train_indices)
    val_data = Subset(full_dataset_val, val_indices)

    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_data, batch_size=batch_size, shuffle=False, num_workers=0)

    logger.info(f"Training split: {len(train_data)} samples | Validation split: {len(val_data)} samples")

    model = build_model(num_classes=len(CLASSES)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    best_val_acc = 0.0
    best_model_weights = copy.deepcopy(model.state_dict())

    start_time = time.time()

    for epoch in range(1, epochs + 1):
        epoch_start = time.time()

        # --- Training Phase ---
        model.train()
        train_loss = 0.0
        train_corrects = 0
        total_train = 0

        for inputs, labels in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            _, preds = torch.max(outputs, 1)

            loss.backward()
            optimizer.step()

            train_loss += loss.item() * inputs.size(0)
            train_corrects += torch.sum(preds == labels.data).item()
            total_train += inputs.size(0)

        epoch_train_loss = train_loss / total_train if total_train > 0 else 0.0
        epoch_train_acc = (train_corrects / total_train * 100.0) if total_train > 0 else 0.0

        # --- Validation Phase ---
        model.eval()
        val_loss = 0.0
        val_corrects = 0
        total_val = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs = inputs.to(device)
                labels = labels.to(device)

                outputs = model(inputs)
                loss = criterion(outputs, labels)
                _, preds = torch.max(outputs, 1)

                val_loss += loss.item() * inputs.size(0)
                val_corrects += torch.sum(preds == labels.data).item()
                total_val += inputs.size(0)

        epoch_val_loss = val_loss / total_val if total_val > 0 else 0.0
        epoch_val_acc = (val_corrects / total_val * 100.0) if total_val > 0 else 0.0

        # Track best weights
        is_best = False
        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            best_model_weights = copy.deepcopy(model.state_dict())
            is_best = True

        elapsed = time.time() - epoch_start
        msg = (
            f"Epoch {epoch}/{epochs} ({elapsed:.1f}s) - "
            f"Loss: {epoch_train_loss:.4f} | "
            f"Train Acc: {epoch_train_acc:.2f}% | "
            f"Val Acc: {epoch_val_acc:.2f}% (Best: {best_val_acc:.2f}%)"
        )
        logger.info(msg)

        if progress_callback:
            progress_callback({
                "status": "training",
                "epoch": epoch,
                "total_epochs": epochs,
                "train_loss": round(epoch_train_loss, 4),
                "train_acc": round(epoch_train_acc, 2),
                "val_loss": round(epoch_val_loss, 4),
                "val_acc": round(epoch_val_acc, 2),
                "best_val_acc": round(best_val_acc, 2),
                "is_best": is_best,
                "message": msg
            })

    # Save best model to designated output path
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    torch.save(best_model_weights, output_path)
    total_time = time.time() - start_time
    logger.info(f"Training completed in {total_time/60:.2f} mins. Saved best weights ({best_val_acc:.2f}%) to: {output_path}")

    summary = {
        "status": "completed",
        "total_epochs": epochs,
        "best_val_acc": round(best_val_acc, 2),
        "saved_path": output_path,
        "elapsed_seconds": round(total_time, 1),
        "message": f"New model trained successfully. Checkpoint saved to {output_path} (Best Val Accuracy: {best_val_acc:.2f}%)."
    }

    if progress_callback:
        progress_callback(summary)

    return summary

def main():
    parser = argparse.ArgumentParser(description="PawCare AI - Dog Disease ResNet18 Training")
    parser.add_argument("--dataset", type=str, default="/Users/apple/Downloads/Dogs", help="Path to dataset directory")
    parser.add_argument("--epochs", type=int, default=15, help="Number of epochs to train")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.0001, help="Learning rate")
    parser.add_argument("--output", type=str, default="models/dog_disease_resnet18_v2.pth", help="Checkpoint output path")
    args = parser.parse_args()

    train_dog_disease_model(
        dataset_dir=args.dataset,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        output_path=args.output
    )

if __name__ == "__main__":
    main()
