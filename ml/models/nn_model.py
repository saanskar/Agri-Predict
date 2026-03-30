"""
@design-guard
role: Train and serve a small neural network classifier for crop recommendation.
layer: service
non_goals:
- Deep architectures; keep training fast for local usage.
boundaries:
  depends_on_layers: [service, domain]
  exposes: [train_neural_net, NeuralNetClassifier]
invariants:
- Input feature dimension must match shared feature schema.
authority:
  decides: [nn_architecture_default, training_defaults]
  delegates: []
extension_policy:
- Change architecture only alongside tests and artifact versioning.
failure_contract:
- Raise on training failures.
testing_contract:
- Unit tests validate forward shape and probability normalization.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import numpy as np
import torch
from numpy.typing import NDArray
from torch import nn


class Net(nn.Module):
    def __init__(self, input_dim: int, output_dim: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(p=0.15),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return cast(torch.Tensor, self.layers(x))


@dataclass(frozen=True)
class NeuralNetClassifier:
    net: Net

    def predict_proba(self, x: NDArray[np.float32]) -> NDArray[np.float32]:
        self.net.eval()
        with torch.no_grad():
            logits = self.net(torch.tensor(x, dtype=torch.float32))
            probs = torch.softmax(logits, dim=1).cpu().numpy().astype(np.float32, copy=False)
        return probs


def train_neural_net(
    x_train: NDArray[np.float32], y_train: NDArray[np.int64], *, seed: int, epochs: int = 25
) -> NeuralNetClassifier:
    torch.manual_seed(seed)
    np.random.seed(seed)

    x = torch.tensor(x_train, dtype=torch.float32)
    y = torch.tensor(y_train, dtype=torch.long)

    input_dim = int(x.shape[1])
    output_dim = int(torch.max(y).item()) + 1

    net = Net(input_dim=input_dim, output_dim=output_dim)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()

    net.train()
    for _ in range(epochs):
        opt.zero_grad(set_to_none=True)
        logits = net(x)
        loss = loss_fn(logits, y)
        loss.backward()
        opt.step()

    return NeuralNetClassifier(net=net)
