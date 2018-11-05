from utils import calculate_prediction_metrics, get_layer_outs, load_data, load_model
import numpy as np


def test_model(model, X_test, Y_test):
    """
    Test a neural network on the MNIST dataset.
    :return: indexes from testing set of correct and incorrect classifications
    """

    # Load saved model
    # model = load_model(model_name)

    # Find activations of each neuron in each layer for each input x in X_test
    layer_outs = get_layer_outs(model, X_test)

    # Print information about the model
    print(model.summary())

    # Evaluate the model
    score = model.evaluate(X_test, Y_test, verbose=0)
    print('[loss, accuracy] -> ' + str(score))

    # Make predictions
    Y_pred = model.predict(X_test)

    # Calculate classification report and confusion matrix
    calculate_prediction_metrics(Y_test, Y_pred, score)

    # Find test and prediction classes
    Y_test_class = np.argmax(Y_test, axis=1)
    Y_pred_class = np.argmax(Y_pred, axis=1)

    classifications = np.absolute(Y_test_class - Y_pred_class)

    # Find correct classifications and misclassifications
    correct_classifications = []
    misclassifications = []
    for i in range(0, len(classifications)):
        if classifications[i] == 0:
            correct_classifications.append(i)
        else:
            misclassifications.append(i)

    print("Testing done!\n")

    return correct_classifications, misclassifications, layer_outs, Y_pred_class


if __name__ == "__main__":
    model = load_model("neural_networks/mnist_test_model_5_30")
    X_train, Y_train, X_test, Y_test = load_data()
    test_model(model, X_test, Y_test)
