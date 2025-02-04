"""
This script performs polynomial regression using either the closed-form solution
or gradient-based optimization techniques. It reads input data from a CSV file,
performs preprocessing, and then executes the chosen regression algorithm.
"""
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def preprocess_data(data_frame: pd.DataFrame) -> tuple:
    """
    Preprocesses the input DataFrame by dropping NaN values, extracting
    the input and output variables, and obtaining column names.

    Args:
    - data_frame: A pandas DataFrame containing input-output data.

    Returns:
    A tuple containing:
    - x_axis: Input variable values reshaped into a 2D numpy array.
    - y_axis: Output variable values reshaped into a 2D numpy array.
    - column_names: List of column names from the DataFrame.
    """
    data_frame = data_frame.dropna()
    x_axis = data_frame.iloc[:, 0].to_numpy().reshape(-1, 1)
    y_axis = data_frame.iloc[:, -1].to_numpy().reshape(-1, 1)
    column_names = data_frame.columns.tolist()
    return x_axis, y_axis, column_names


def save_equation(coefficients: list) -> None:
    """
    Saves the equation generated by the regression model to a text file.

    Args:
    - coefficients: List of coefficients representing the equation.

    Returns:
    None
    """
    terms = []
    for i, coefficient in enumerate(coefficients):
        if coefficient != 0:
            term = f"{coefficient} * x^{i}"
            terms.append(term)
    equation = "y = " + " + ".join(terms)

    with open("equation.txt", "w", encoding="utf-8") as file:
        file.write(equation)


def plot(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray,
         y_prediction: np.ndarray, column_names: list) -> None:
    """
    Plots the training data points along with the predicted values.

    Args:
    - x_train: Training set of input variables.
    - y_train: Training set of output variables.
    - x_test: Testing set of input variables.
    - y_prediction: Predicted values corresponding to x_test.
    - column_names: List of column names from the DataFrame.

    Returns:
    None
    """
    plt.scatter(x_train, y_train, color="blue")
    plt.plot(x_test, y_prediction, color="red")
    is_polynomial = DEGREE_OF_POLYNOMIAL > 1
    title = f"Polynomial Regression (degree {DEGREE_OF_POLYNOMIAL})" \
        if is_polynomial else "Linear Regression"
    plt.title(title)
    plt.xlabel(column_names[0])
    plt.ylabel(column_names[-1])
    plt.savefig("plot.png")
    plt.show()


def gradient_based_polynomial_regression(data: np.ndarray) -> tuple:
    """
    Performs polynomial regression using gradient-based optimization.

    Args:
    - data: A numpy array containing input-output data.

    Returns:
    A tuple containing:
    - x_train: Training set of input variables.
    - y_train: Training set of output variables.
    - x_test: Testing set of input variables.
    - y_prediction: Predicted values corresponding to x_test.
    - model: Trained linear regression model.
    """
    x_train, x_test, y_train, _ = train_test_split(data[:, :-1],
                                                   data[:, -1], test_size=0.2, random_state=0)

    polynomial_features = PolynomialFeatures(degree=DEGREE_OF_POLYNOMIAL)
    x_train_polynomial = polynomial_features.fit_transform(x_train)
    x_test_polynomial = polynomial_features.transform(x_test)

    model = LinearRegression()
    model.fit(x_train_polynomial, y_train)

    y_prediction = model.predict(x_test_polynomial)

    x_test, y_prediction = x_test[np.argsort(x_test.flatten())], \
        y_prediction[np.argsort(x_test.flatten())]

    return x_train, y_train, x_test, y_prediction, model


def closed_form_polynomial_regression(data: np.ndarray, degree: int) -> tuple:
    """
    Performs polynomial regression using closed-form solution.

    Args:
    - data: A numpy array containing input-output data.
    - degree: Degree of the polynomial features.

    Returns:
    A tuple containing:
    - x_train: Training set of input variables.
    - y_train: Training set of output variables.
    - x_test: Testing set of input variables.
    - y_prediction: Predicted values corresponding to x_test.
    - coefficient: Coefficients of the polynomial regression equation.
    """
    x_train, x_test, y_train, _ = train_test_split(data[:, :-1],
                                                   data[:, -1], test_size=0.2, random_state=0)

    x_test_polynomial = np.c_[np.ones(x_test.shape[0]), x_test]
    x_train_polynomial = np.c_[np.ones(x_train.shape[0]), x_train]
    for i in range(2, degree + 1):
        x_test_polynomial = np.c_[x_test_polynomial, x_test ** i]
        x_train_polynomial = np.c_[x_train_polynomial, x_train ** i]

    coefficient = np.dot(np.linalg.inv(np.dot(x_train_polynomial.T, x_train_polynomial)),
                         np.dot(x_train_polynomial.T, y_train))

    y_prediction = np.dot(x_test_polynomial, coefficient)

    x_test, y_prediction = x_test[np.argsort(x_test.flatten())], \
        y_prediction[np.argsort(x_test.flatten())]

    return x_train, y_train, x_test, y_prediction, coefficient


def regression() -> None:
    """
    Orchestrates the regression process based on user input from command line.

    Args:
    None

    Returns:
    None
    """
    data_frame = pd.read_csv(INPUT_FILE_PATH)
    x_axis, y_axis, column_names = preprocess_data(data_frame)
    data = np.concatenate((x_axis, y_axis), axis=1)

    if ALGORITHM_TYPE == "closed":
        x_train, y_train, x_test, y_prediction, coefficient = \
            closed_form_polynomial_regression(data, DEGREE_OF_POLYNOMIAL)
        save_equation(coefficient.flatten())
        plot(x_train, y_train, x_test, y_prediction, column_names)
    elif ALGORITHM_TYPE == "gradient":
        x_train, y_train, x_test, y_prediction, model = gradient_based_polynomial_regression(data)
        coefficients = model.coef_
        coefficients[0] += model.intercept_
        save_equation(coefficients.flatten())
        plot(x_train, y_train, x_test, y_prediction, column_names)
    else:
        print("Invalid algorithm type. Please choose 'closed' or 'gradient'.")


if len(sys.argv) != 4:
    print("Try again! Enter: python [script.py]"
          " [input_file_path] [type_of_algorithm(closed or gradient)] [degree_of_polynomial]")
    sys.exit(1)

INPUT_FILE_PATH: str = sys.argv[1]
ALGORITHM_TYPE: str = sys.argv[2]
DEGREE_OF_POLYNOMIAL: int = int(sys.argv[3])

regression()
