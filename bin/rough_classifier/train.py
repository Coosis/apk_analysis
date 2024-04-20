import os
import yaml
import torch
from rough_classifier import RoughTransformer as rt

# number of epochs to train the model
n_epochs = 100
# after every eval_interval epochs, calculate the loss on the training and validation data
eval_interval = 500
# number of iterations to estimate the loss
eval_iters = 10

parent_dir = os.path.dirname(os.path.dirname(__file__))
data_dir = os.path.join(os.path.dirname(__file__), 'data')

def get_batch(mode, data, batch_size, device):
    """
    :param mode: str: 'train' or 'val'
    :param data: list: list of app names
    :return: tuple: (X, Y_binary, Y_classification) where X is the input tensor of shape (batch_size, block_size)
    """
    length = len(data)
    split = int(0.8 * length)
    if mode == 'train':
        data = data[:split]
    else:
        data = data[split:]
    idx = torch.randint(0, len(data), (batch_size,))
    Xs = []
    Y_binarys = []
    Y_classifications = []
    for i in idx:
        with open(os.path.join(data_dir, data[i], "api.txt"), 'r') as f:
            X = torch.tensor([int(line.strip()) for line in f])
            Xs.append(X)
        with open(os.path.join(data_dir, data[i], "classification.txt"), 'r') as f:
            Y_binary_list = []
            Y_classification_list = []
            for i, line in enumerate(f):
                if i == 0 or i == 1:
                    Y_binary_list.append(int(line.strip()))
                else:
                    Y_classification_list.append(int(line.strip()))
            Y_binarys.append(torch.tensor(Y_binary_list))
            Y_classifications.append(torch.tensor(Y_classification_list))

    X = torch.stack(Xs).to(device)
    Y_binary = torch.stack(Y_binarys).to(device)
    Y_classification = torch.stack(Y_classifications).to(device)

    return X, Y_binary, Y_classification

@torch.no_grad()
def estimate_loss(model, batch_size, device):
    out = {}
    model.eval()
    data = os.listdir(data_dir)
    for split in ['train', 'val']:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Yb, Yc = get_batch(split, data, batch_size, device)
            logits, loss = model(X, Yb, Yc)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out

def main():
    checkpoint = input("Checkpoint to load(default: None): ")
    checkpoint = f"checkpoint_{checkpoint}.pth" if checkpoint else None
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if os.path.exists(os.path.join(data_dir, 'hyperparameters.yaml')):
        hyperparameters = yaml.safe_load(open(os.path.join(data_dir, 'hyperparameters.yaml'), 'r'))
    else:
        print("Hyperparameters file not found in data directory. Loading default parameters.")
        hyperparameters = yaml.safe_load(open(os.path.join(parent_dir, 'hyperparameters.yaml'), 'r'))
        with open(os.path.join(data_dir, 'hyperparameters.yaml'), 'w') as f:
            yaml.dump(hyperparameters, f)

    vocab_size = hyperparameters['vocab_size']
    group_num = hyperparameters['group_num']
    n_blocks = hyperparameters['n_blocks']
    n_embd = hyperparameters['n_embd']
    n_head = hyperparameters['n_head']
    dropout = hyperparameters['dropout']
    model = rt(vocab_size, group_num, n_blocks, n_embd, n_head, dropout, device=device)

    batch_size = hyperparameters['batch_size']

    if checkpoint:
        model_path = os.path.join(data_dir, checkpoint)
        model.load_state_dict(torch.load(model_path))

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    for epoch in range(n_epochs):
        if epoch % eval_interval or epoch == eval_interval - 1:
            losses = estimate_loss(model, batch_size, device)
            print(f"step {iter}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")
            state_dict = model.state_dict()
            torch.save(state_dict, f"checkpoint_{epoch}.pth")

        # get the batch
        idx, binary, classification = get_batch('train', os.listdir(data_dir), batch_size, device)
        optimizer.zero_grad()
        binary_loss, classification_loss = model(idx, binary, classification)
        loss = binary_loss + classification_loss
        loss.backward()

if __name__ == '__main__':
    main()
