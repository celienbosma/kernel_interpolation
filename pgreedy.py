import numpy as np
import random
import math
import matplotlib.pyplot as plt


def pgreedy(discrete_omega, kernel, f, maxIter):
	""" For a surrogate model sf for model f: Omega \subset R^d -> R^q,
		the coefficients of the expansion wrt a kernel basis is computed.
		Assuming:
			- discrete_omega is an np.array of numbers in Omega (R^d), here d = 1
			- kernel is a function from Omega x Omega to real numbers
			- f is an np.array of shape (len(discrete_omega), q),
				where q is the output dimension, containing the function
				evaluations of discrete_omega
	"""

	domega_size = len(discrete_omega)
	q = f.shape[1]

	def A(i, j):
		if type(i) is list or type(i) is np.ndarray:
			rows = np.array([])
			for row_index in i:
				row = np.array([])
				if type(j) is list or type(j) is np.ndarray:
					for column_index in j:
						row = np.append(row, kernel(discrete_omega[row_index], discrete_omega[column_index]))
				else:
					row = np.append(row, kernel(discrete_omega[row_index], discrete_omega[j]))
				rows = np.append(rows, row)
			result = rows.reshape(len(i), -1)
		else:
			result = kernel(discrete_omega[i], discrete_omega[j])
		return result


	# initializing needed variables

	# selected indices
	selected = []
	# not selected indices
	notselected = range(0, domega_size)
	# a 2-d array of the Newton basis evaluated on discrete_omega
	basis_eval = np.zeros((domega_size, maxIter))
	# an array of the coefficients wrt the Newton basis
	coeff = np.zeros((maxIter, q))
	# the residual evaluated on discrete_omega at each iteration
	residual_eval = np.copy(f)
	# the power function evaluated on discrete_omega at each iteration
	power_eval = A(0,0) * np.ones(domega_size)
	# the basis transition matrix
	change_of_basis = np.zeros((maxIter, maxIter))
	# an array storing the maximum power function at each iteration
	pmax = np.zeros(maxIter)


	for k in range(0, maxIter):
		# point selection of this iteration
		i = np.argmax(power_eval[notselected])
		selected.append(notselected[i])
		pmax[k] = power_eval[notselected[i]]

		# computing the kth basis function
		if k > 0:
			a = np.transpose(basis_eval[notselected, 0:k]).reshape((k, len(notselected)))
			b = basis_eval[selected[k], 0:k]
			basis_eval[notselected, k] = A(notselected, selected[k]).reshape(len(notselected)) - np.dot(b, a)
			# Problem: 2-d arrays mit shape( _ , 1) werden automatisch als Zeilenvektor gespeichert
		else:
			basis_eval[notselected, k] = A(notselected, selected[k]).reshape(len(notselected))
		basis_eval[notselected, k] /= power_eval[selected[k]]

		# computing the kth coefficient wrt the Newton basis
		coeff[k, :] = residual_eval[selected[k], :] / power_eval[selected[k]]

		# updating the residuals
		x = residual_eval[notselected, :].reshape(len(notselected), q)
		y = basis_eval[notselected, k].reshape(len(notselected), 1)
		z = coeff[k, :].reshape(1,q)
		residual_eval[notselected, :] = np.subtract(x, np.matmul(y, z))

		# updating the basis transition matrix
		change_of_basis[0:k, k] = - np.dot(np.copy(change_of_basis[0:k, 0:k]), np.copy(np.transpose(basis_eval[selected[k], 0:k])))
		change_of_basis[k, k] = 1
		change_of_basis[:, k] /= np.copy(power_eval[selected[k]])

		#updating the power function
		abs_vector = np.vectorize(math.fabs)
		power_squared = np.square(power_eval[notselected])
		basis_squared = np.square(basis_eval[notselected, k])
		power_eval[notselected] = np.sqrt(abs_vector(power_squared - basis_squared))

		del notselected[i]

	print "indices of selection: "
	print selected

	# resulting approximation of discrete_omega
	sf = np.dot(coeff.reshape(1, maxIter), np.transpose(basis_eval[:, :])).reshape(-1)
	# computing the coefficients wrt the kernel basis
	a = np.dot(change_of_basis, coeff)
	sfa = np.dot(A(range(0, domega_size), selected), a).reshape(-1)

	# plotting the training
	plt.figure(1)
	plt.title("model: blue line, surrogate: green dots (not selected), red dots (selected)")
	plt.plot(discrete_omega, f, discrete_omega, sf, 'g^', discrete_omega[selected], sf[selected], 'r^')
	plt.figure(2)
	plt.title("residuals")
	plt.plot(discrete_omega, residual_eval, 'bo', discrete_omega[selected], residual_eval[selected], 'ro')
	plt.figure(3)
	plt.title("maximum of the evaluated power function at each iteration on discrete_omega")
	plt.plot(range(0,maxIter), pmax, 'r^')
	plt.show()

	return [a, discrete_omega[selected]]

# Test
if __name__ == "__main__":
	discrete_omega = np.linspace(-3.0, 3.0,50)
	# = np.array([])
	# for i in range(0, 10):
		# discrete_omega = np.append(discrete_omega, random.random())
	print "discrete_omega: "
	print discrete_omega
	def kernel(x,y):
		return math.exp(-math.pow(x-y, 2))
	# some test function
	sin_vector = np.vectorize(math.sin)
	f = sin_vector(discrete_omega).reshape((-1, 1))

	# computing the basis
	[a, selection] = pgreedy(discrete_omega, kernel, f, 20)