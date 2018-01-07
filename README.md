# DeepLearning-on-NotMNIST
A further tuning on the codes from Udacity course on deep learning (https://www.udacity.com/course/deep-learning--ud730)

The input is the image of first 10 alphabets and the output is the relaization of the alphabet. More information on NotMNIST data can be found in (http://yaroslavvb.blogspot.ca/2011/09/notmnist-dataset.html).

Acheiving higher test accuracies is harder in this data set compared to the MNIST data set.

This code acheives 95.8% test accuracy with using RBFs, SGD with linear decay learning rate, and regularization. There is two hidden layers of 300 and 50 size.

The first file downloads and pickles the file, and the second one does the analysis.
