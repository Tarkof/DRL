import numpy as np

def preprocessing(X):
    X = X.flatten()
    return X

def one_hot(move):
    if type(move) is type(2):
        return np.eye(8)[move] #TODO should be MLP.input_shape but hardcoding until better solution
    return np.eye(move.shape[0])[np.argmax(move)]

def softmax_ind(X, ind):
    return np.exp(X[ind]) / np.sum(np.exp(X), axis=-1)

def softmax(X):
    return np.array([softmax_ind(X, i) for i,_ in enumerate(X)])

def deriv_softmax_ind(X, ind):
    return np.exp(X[ind]) * np.sum(np.exp([x for i,x in enumerate(X) if i!=ind] ), axis=-1) / np.square(np.sum(np.exp(X), axis=-1))

def deriv_softmax(X):
    return np.array([deriv_softmax_ind(X, i) for i,_ in enumerate(X)])

def sigmoid(X):
    return 1 / (1 + np.exp(-X))

def deriv_sigmoid(X):
    return sigmoid(X) * (1 - sigmoid(X))

def deriv_cross_entropy(y_pred, y_true):
    ind = np.argmax(y_true)
    y = one_hot(y_true)
    return  -y / y_pred[ind]

class MLP():
    """
    A Multi-Layer Perceptron, also called Fully Connected Neural Network to decide the policy
    for the RL framework.

    Should be fed with a frame from the game and outputs a number between 0 and 7 corresponding
    to the direction the player should move in.
    """
    def __init__(self, input_shape, hidden_shape, output_shape=8, learning_rate=0.0001):
        self.Wh = np.random.uniform(low=-0.01, high=0.01, size=(np.prod(input_shape), hidden_shape))
        self.Bh = np.zeros(hidden_shape)
        self.Wo = np.random.uniform(low=-0.01, high=0.01, size=(hidden_shape, output_shape))
        self.Bo = np.zeros(output_shape)
        self.learning_rate = learning_rate
        return

    def forward(self, X):
        _,y_pred = self.forward_keep_activations(X)
        return y_pred


    def forward_keep_activations(self, X):
        zh = np.dot(X, self.Wh) + self.Bh
        activation_h = sigmoid(zh)
        zo = np.dot(activation_h, self.Wo) + self.Bo
        y_pred = softmax(zo)
        return activation_h, y_pred

    #Implement Negative Log Likehood (also called cross-entropy)
    def cross_entropy(self, y_pred, y_true):
        return -np.mean(np.sum(y_true * np.log(y_pred), axis=-1))

    def gradients(self, X, act_h, y_pred, y_true): #Compute gradients for weights and biases using Chain rule
        deriv_y_pred = y_pred - y_true
        grad_wo = np.outer(act_h , deriv_y_pred)
        grad_bo = deriv_y_pred
        deriv_zo = np.dot(self.Wo, deriv_y_pred)
        zh = np.dot(X, self.Wh) + self.Bh 
        deriv_act_h = deriv_sigmoid(zh) * deriv_zo
        grad_wh = np.outer(X , deriv_act_h)
        grad_bh = deriv_act_h
        return {"grad_wo" : grad_wo, "grad_bo" : grad_bo, "grad_wh" : grad_wh, "grad_bh" : grad_bh}

    def backward(self, grad): #TODO
        self.Wo -= (self.learning_rate * grad["grad_wo"])
        self.Bo -= (self.learning_rate * grad["grad_bo"])
        self.Wh -= (self.learning_rate * grad["grad_wh"])
        self.Bh -= (self.learning_rate * grad["grad_bh"])

    def train(self, X, y_true): #TODO
        act_h, y_pred = self.forward_keep_activations(X)
        grads = self.gradients(X, act_h, y_pred, y_true)
        self.backward(grads)
        pass #Iterate cross-entropy over batch of data and backpropagate accordingly

    def predict(self, X): #TODO
        # Use final weights and biases to compute prediction for given input
        return np.argmax(self.forward(X))