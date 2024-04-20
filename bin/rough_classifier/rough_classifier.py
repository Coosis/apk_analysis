import torch
import torch.nn as nn
import torch.nn.functional as F

class Head(nn.Module):
    """
    Single attention head.
    """
    def __init__(self, n_embd, head_size, dropout):
        """
        :param n_embd: int: number of embedding dimensions
        :param head_size: int: number of dimensions in the head
        :param dropout: float: dropout rate
        """
        super().__init__()
        self.q = nn.Linear(n_embd, head_size, bias=False)
        self.k = nn.Linear(n_embd, head_size, bias=False)
        self.v = nn.Linear(n_embd, head_size, bias=False)
        self.dropout = nn.Dropout(dropout)
        self.head_size = head_size

    def forward(self, x):
        """
        :param x: torch.Tensor: input tensor of shape (batch_size, block_size, n_embd)
        """
        # x is of shape (batch_size, block_size, n_embd)
        B, T, C = x.shape
        # generating queries, keys and values
        # k, q, v are of shape (batch_size, block_size, head_size)
        q = self.q(x)
        k = self.k(x)
        v = self.v(x)
        # wei is of shape (batch_size, block_size, block_size)
        wei = q @ k.transpose(-2, -1) * (self.head_size ** -0.5)
        wei = F.softmax(wei, dim=-1)
        wei = self.dropout(wei)
        return wei @ v

class MultiattentionHead(nn.Module):
    """
    Multi-head attention.
    """
    def __init__(self, n_embd, n_head, head_size, dropout):
        """
        :param n_embd: int: number of embedding dimensions
        :param n_head: int: number of head. must be divisible by n_embd
        :param head_size: int: number of dimensions in the head
        :param dropout: float: dropout rate
        """
        super().__init__()
        self.heads = nn.ModuleList([Head(n_embd, head_size, dropout) for _ in range(n_head)])
        self.proj = nn.Linear(n_head * head_size, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        """
        :param x: torch.Tensor: input tensor of shape (batch_size, block_size, n_embd)
        """
        # (batch_size, block_size, n_embd)
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        out = self.dropout(self.proj(out))
        return out

# Feed Forward
class FeedForward(nn.Module):
    def __init__(self, n_embd, dropout):
        """
        :param n_embd: int: number of embedding dimensions
        :param dropout: float: dropout rate
        """
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, n_embd * 4),
            nn.ReLU(),
            nn.Linear(n_embd * 4, n_embd),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        """
        :param x: torch.Tensor: input tensor of shape (batch_size, block_size, n_embd)
        """
        # (batch_size, block_size, n_embd)
        return self.net(x)

# Transformer Block
class Block(nn.Module):
    def __init__(self, n_embd, n_head, head_size, dropout):
        """
        :param n_embd: int: number of embedding dimensions
        :param block_size: int: number of tokens in the content
        :param n_head: int: number of head. must be divisible by n_embd
        :param head_size: int: number of dimensions in the head
        :param dropout: float: dropout rate
        """
        super().__init__()
        self.sa = MultiattentionHead(n_embd, n_head, head_size, dropout)
        self.ffwd = FeedForward(n_embd, dropout)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)
    
    def forward(self, x):
        """
        :param x: torch.Tensor: input tensor of shape (batch_size, block_size, n_embd)
        """
        # (batch_size, block_size, n_embd)
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x

class BinaryClassificationHead(nn.Module):
    def __init__(self, n_embd):
        """
        :param n_embd: int: number of embedding dimensions
        """
        super().__init__()
        self.fc = nn.Linear(n_embd, 2)
        self.actv = nn.Sigmoid()

    def forward(self, x):
        """
        :param x: torch.Tensor: input tensor of shape (batch_size, block_size, n_embd)
        """
        # (batch_size, block_size, 2)
        x = self.fc(x)
        return self.actv(x)

class Classifier(nn.Module):
    def __init__(self, n_embd, group_num):
        """
        :param n_embd: int: number of embedding dimensions
        :param group_num: int: number of groups
        """
        super().__init__()
        self.fc = nn.Linear(n_embd, group_num)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        """
        :param x: torch.Tensor: input tensor of shape (batch_size, block_size, n_embd)
        """
        x = self.fc(x)
        return self.softmax(x)

# Transformer
class RoughTransformer(nn.Module):
    def __init__(self, vocab_size, group_num, n_blocks, n_embd, n_head, dropout, device):
        """
        :param vocab_size: int: number of tokens in the vocabulary
        :param group_num: int: number of groups
        :param n_blocks: int: number of transformer blocks
        :param n_embd: int: number of embedding dimensions
        :param n_head: int: number of head. must be divisible by n_embd
        :param dropout: float: dropout rate
        :param device: torch.device: device to run the model on, either 'cpu' or 'cuda'
        """
        super().__init__()
        head_size = n_embd // n_head
        self.embd_table = nn.Embedding(vocab_size, n_embd)
        self.blocks = nn.Sequential(*[Block(n_embd, n_head, head_size, dropout) for _ in range(n_blocks)])
        self.lnf = nn.LayerNorm(n_embd)
        self.binary_head = BinaryClassificationHead(n_embd)
        self.binary_loss = nn.BCELoss()
        self.classifier = Classifier(n_embd, group_num)
        self.classification_loss = nn.CrossEntropyLoss()
        self.device = device

        # recursively apply the initialization function to every submodule
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, binary=None, classification=None):
        """
        :param idx: torch.Tensor: input tensor of shape (batch_size, block_size)
        """
        # (batch_size, block_size)
        B, T = idx.shape
        # (batch_size, block_size, n_embd)
        x = self.embd_table(idx)
        # (batch_size, block_size, n_embd)
        x = self.blocks(x)
        # (batch_size, block_size, n_embd)
        x = self.lnf(x)
        # (batch_size, block_size, 2)
        binary_logits = self.binary_head(x)
        # (batch_size, block_size, group_num)
        classification_logits = self.classifier(x)

        if binary == None or classification == None:
            binary_loss = 0
            classification_loss = 0
        else:
            binary_logits = binary_logits.view(B * T, 2)
            binary = binary.view(B * T)
            binary_loss = self.binary_loss(binary_logits, binary)
            classification_logits = classification_logits.view(B * T, 2)
            classification = classification.view(B * T)
            classification_loss = self.classification_loss(classification_logits, classification)

        return binary_loss, classification_loss

