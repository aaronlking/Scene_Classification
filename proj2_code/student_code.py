from collections.abc import Sized
import numpy as np
from numpy.random import default_rng
import skimage
import torch
import cv2
from skimage.transform import resize
from proj2_code.feature_matching.SIFTNet import get_siftnet_features


def pairwise_distances(X, Y):
    """
    This method will be very similar to the pairwise_distances() function found
    in sklearn
    (https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise_distances.html)
    However, you are NOT allowed to use any library functions like this
    pairwise_distances or pdist from scipy to do the calculation!

    The purpose of this method is to calculate pairwise distances between two
    sets of vectors. The distance metric we will be using is 'euclidean',
    which is the square root of the sum of squares between every value.
    (https://en.wikipedia.org/wiki/Euclidean_distance)

    Useful functions:
    -   np.linalg.norm()

    Args:
    -   X: N x d numpy array of d-dimensional features arranged along N rows
    -   Y: M x d numpy array of d-dimensional features arranged along M rows

    Returns:
    -   D: N x M numpy array where d(i, j) is the distance between row i of X and
        row j of Y
    """
    N, d_y = X.shape
    M, d_x = Y.shape
    assert d_y == d_x

    # D is the placeholder for the result
    D = None

    ###########################################################################
    # TODO: YOUR CODE HERE                                                    #
    ###########################################################################

    D = np.zeros(shape=(N, M))
    for i in range(N):
        for j in range(M):
            D[i][j] = np.linalg.norm(Y[j]-X[i])
    return D

    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return np.array(D)


def get_tiny_images(image_arrays):
    """
    This feature is inspired by the simple tiny images used as features in
    80 million tiny images: a large dataset for non-parametric object and
    scene recognition. A. Torralba, R. Fergus, W. T. Freeman. IEEE
    Transactions on Pattern Analysis and Machine Intelligence, vol.30(11),
    pp. 1958-1970, 2008. http://groups.csail.mit.edu/vision/TinyImages/

    To build a tiny image feature, simply resize the original image to a very
    small square resolution, e.g. 16x16. You can either resize the images to
    square while ignoring their aspect ratio or you can crop the center
    square portion out of each image. Making the tiny images zero mean and
    unit length (normalizing them) will increase performance modestly.

    Useful functions:
    -   skimage.transform.resize
    -   cv2.resize
    -   ndarray.flatten()

    Args:
    -   image_arrays: list of N elements each containing image as Numpy array, in
                grayscale

    Returns:
    -   feats: N x d numpy array of resized and then vectorized tiny images
                e.g. if the images are resized to 16x16, d would be 256
    """
    # For this part in order to pass the unit test, load the image in
    # grayscale, resize it to 16x16, and return the Numpy array

    # dummy feats variable
    feats = []

    ###########################################################################
    # TODO: YOUR CODE HERE                                                    #
    ###########################################################################
#     reprint(image_arrays[0].shape)

    for i in image_arrays:
        feats.append(cv2.resize(i ,dsize=(16,16))) #change to 8x8
    feats = np.array(feats)
    N,x,y = feats.shape
    feats = np.reshape(feats,(N,256))

    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return feats


def nearest_neighbor_classify(train_image_feats, train_labels,
                              test_image_feats, k=3):#change this
    """
    This function will predict the category for every test image by finding
    the training image with most similar features. Instead of 1 nearest
    neighbor, you can vote based on k nearest neighbors which will increase
    performance (although you need to pick a reasonable value for k).
    Useful functions:
    -   D = pairwise_distances(X, Y)
          computes the distance matrix D between all pairs of rows in X and Y.
            -  X is a N x d numpy array of d-dimensional features arranged along
            N rows
            -  Y is a M x d numpy array of d-dimensional features arranged along
            N rows
            -  D is a N x M numpy array where d(i, j) is the distance between row
            i of X and row j of Y
    - np.argsort to find the indices corresponding to a sorting
    - np.unique to find counts of unique occurrences
    Args:
    -   train_image_feats:  N x d numpy array, where d is the dimensionality of
            the feature representation
    -   train_labels: N element list, where each entry is a string indicating
            the ground truth category for each training image
    -   test_image_feats: M x d numpy array, where d is the dimensionality of the
            feature representation.
    -   k: the k value in kNN, indicating how many votes we need to check for
            the label
    Returns:
    -   test_labels: M element list, where each entry is a string indicating the
            predicted category for each testing image
    """
    test_labels = []

    ###########################################################################
    # TODO: YOUR CODE HERE                                                    #
    ###########################################################################

    label_array_size, d = test_image_feats.shape #label_array_size is 3 and d is 128 in the first test
    D = pairwise_distances(test_image_feats, train_image_feats)
    for i in range(label_array_size): # i iterates from 0 - 2
        sorted_distances = np.argsort(D[i])
        first_K_sorted_distances_indices = sorted_distances[0:k]
        classification = []
        for j in range(k):
            classification.append(train_labels[first_K_sorted_distances_indices[j]])
        values, counts = np.unique(classification, return_counts = True)
        maxIndex = np.argmax(counts)
        test_labels.append(values[maxIndex])
        
    #############################################################################
    #                             END OF YOUR CODE                              #
    #############################################################################
    # print("total possible: ", len(set(test_labels)))
    return test_labels


def kmeans(feature_vectors, k, max_iter = 100):
    """
    Implement the k-means algorithm in this function. Initialize your centroids
    with random *unique* points from the input data, and repeat over the
    following process:
    1. calculate the distances from data points to the centroids
    2. assign them labels based on the distance - these are the clusters
    3. re-compute the centroids from the labeled clusters

    During the iterations, if any of the cluster centers has no data points associated with it, replace it with a random data point.

    Please note that you are NOT allowed to use any library functions like
    vq.kmeans from scipy or kmeans from vlfeat to do the computation!

    Useful functions:
    -   np.random.choice
    -   np.random.randint
    -   np.argmin / np.argsort
    -   pairwise_distances
    -   np.linalg.norm


    Args:
    -   feature_vectors: the input data collection, a Numpy array of shape (N, d)
            where N is the number of features and d is the dimensionality of the
            features
    -   k: the number of centroids to generate, of type int
    -   max_iter: the total number of iterations for k-means to run, of type int

    Returns:
    -   centroids: the generated centroids for the input feature_vectors, a Numpy
            array of shape (k, d)
    """

    # dummy centroids placeholder
    centroids = None

    #############################################################################
    # TODO: YOUR CODE HERE                                                      #
    #############################################################################

    N, M = feature_vectors.shape

    random_unique_data = np.random.choice(N, k, replace = False)
    centroids = feature_vectors[random_unique_data, :]
    D = pairwise_distances(feature_vectors, centroids)
    clusters = np.array(np.argmin(D, axis=1))
    
    for i in range(max_iter):
        centroids = []
        for j in range(k):
            updated_centroids = feature_vectors[clusters == j].mean(axis = 0)
            
            if(np.isnan(updated_centroids).all()): #check for nan
                updated_random_unique_data = np.random.choice(N, 1, replace = False)
                updated_centroids = feature_vectors[updated_random_unique_data, :]
            centroids.append(updated_centroids)
            
        centroids = np.vstack(centroids)
        D = pairwise_distances(feature_vectors, centroids)
        clusters = np.array(np.argmin(D, axis=1))
        
    #############################################################################
    #                             END OF YOUR CODE                              #
    #############################################################################
    return centroids


def build_vocabulary(image_arrays, vocab_size, stride = 20):
    """
    Overview:
    This function will sample SIFT descriptors from the training images,
    cluster them with kmeans, and then return the cluster centers.

    Details:
     1. image_arrays contains the list of images in the training set from which
     the vocabulary will be built.

     2. For each training image, get some SIFT descriptors. You will need to pass the locations (x, y)
    (at which SIFT descriptor needs to be computed) to the function get_siftnet_features().
        Note: In order to pass the unit test, leave out a 10-pixel margin in the image,
        that is, start your x and y from 10, and stop at (image_width - 10) and
        (image_height - 10), before feeding to the function get_siftnet_features()

    3. Once you have tens of thousands of SIFT features from many training
    images, cluster them with kmeans. The resulting centroids are now your
    visual word vocabulary.

    Note that the default vocab_size of 50 is sufficient for you to get a decent
    accuracy (>40%), but you are free to experiment with other values.

    Efficiency Notes:
    -  To save computation time, you don't necessarily need to sample from all images in Step 1,
    although it would be better to do so.

    - Once you get the descriptors from each image in step 2, you can randomly sample a subset
    to save memory and speed up the clustering. This is because you're only trying to get a
    representative sample here.

    - For testing purposes, you may experiment with larger stride (when sampling x and y locations)
     so that you just compute fewer points and check the result quickly.


    Useful functions:
    -   np.array(img, dtype='float32') to convert each input image to float32 (required by siftnet)
    -   torch.from_numpy(img_array), and
            img_tensor = img_tensor.reshape(
                (1, 1, img_array.shape[0], img_array.shape[1]))
            for converting a numpy array to a torch tensor for siftnet
    -   get_siftnet_features() from SIFTNet: you can pass in the image tensor in
            grayscale, together with the sampled x and y positions (as 1D numpy arrays)
            to obtain the SIFT features (see next)
    -   np.arange() and np.meshgrid(): for you to generate the sample x and y
            positions faster. Use reshape method to reshape the coordinates to 1D.

    Args:
    -   image_arrays: list of images in Numpy arrays, in grayscale
    -   vocab_size: size of vocabulary
    -   stride: the stride of your SIFT sampling (i.e. the interval at which x and y are sampled in step 2)

    Returns:
    -   vocab: This is a (vocab_size, dim) Numpy array (vocabulary). Where dim
            is the length of your SIFT descriptor. Each row is a cluster center
            / visual word.
    """

    dim = 128  # length of the SIFT descriptors that you are going to compute.
    vocab = None

    ###########################################################################
    # TODO: YOUR CODE HERE                                                    #
    ###########################################################################
#1,2) for each training image, get SIFT descriptors
    #1,2) for each training image, get SIFT descriptors
    SIFT_descriptors = np.array([])
    for image in image_arrays:        
        #convert each input image to float32
        float_img = np.array(image, dtype='float32')
        
        #2) storing np array image as a tensor
        #should parameter be img_array?
        t = torch.from_numpy(float_img) 
        
        #reshape tensor
        #should parameters be image or img_array or image_arrays?
        img_tensor = t.reshape((1, 1, image.shape[0], image.shape[1])) 
        
        #get x and y coordinates for get_siftnet_features() function
        y, x = np.arange(10,image.shape[1]-10, step=stride), np.arange(10,image.shape[0]-10, step=stride)
        x,y = np.meshgrid(y,x)
        x = x.flatten()
        y = y.flatten()
        
        #get SIFT descriptors
        SIFT_descriptors = np.append(SIFT_descriptors, get_siftnet_features(img_tensor, x, y))
    SIFT_descriptors = SIFT_descriptors.reshape(-1,dim)
    #3) cluster SIFT features with kmeans()
    #kmeans(feature_vectors, k, max_iter = 100)
    vocab = kmeans(SIFT_descriptors, vocab_size)#100 is the default in the kmeans parameter

    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return vocab


def kmeans_quantize(raw_data_pts, centroids):
    """
    Implement the k-means quantization in this function. Given the input data
    and the centroids, assign each of the data entry to the closest centroid.

    Useful functions:
    -   pairwise_distances
    -   np.argmin

    Args:
    -   raw_data_pts: the input data collection, a Numpy array of shape (N, d)
            where N is the number of input data, and d is the dimension of it,
            given the standard SIFT descriptor, d = 128
    -   centroids: the generated centroids for the input feature_vectors, a
            Numpy array of shape (k, d), where k is the number of clusters
            previously obtained

    Returns:
    -   indices: the index of the centroid which is closest to the data points,
            a Numpy array of shape (N, )

    """
    indices = None

    ###########################################################################
    # TODO: YOUR CODE HERE                                                    #
    ###########################################################################
    distances = pairwise_distances(centroids, raw_data_pts)
    indices = np.argmin(distances, axis = 0)
    

    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return indices


def get_bags_of_sifts(image_arrays, vocabulary, step_size = 10):
    """

    You will want to construct SIFT features here in the same way you
    did in build_vocabulary() (except for possibly changing the sampling
    rate) and then assign each local feature to its nearest cluster center
    and build a histogram indicating how many times each cluster was used.
    Don't forget to normalize the histogram, or else a larger image with more
    SIFT features will look very different from a smaller version of the same
    image.

    Useful functions:
    -  np.array(img, dtype='float32'), torch.from_numpy(img_array), and
            img_tensor = img_tensor.reshape(
                (1, 1, img_array.shape[0], img_array.shape[1]))
            for converting a numpy array to a torch tensor for siftnet
    -   get_siftnet_features() from SIFTNet: you can pass in the image tensor
            in grayscale, together with the sampled x and y positions to obtain
            the SIFT features
    -   kmeans_quantize: to assign each descriptor to its nearest cluster center
    -   np.histogram() or np.bincount(): easy way to help you calculate for a
            particular image, how the visual words span across the vocab


    Args:
    -   image_arrays: A list of input images in Numpy array, in grayscale
    -   vocabulary: A numpy array of dimensions:
            vocab_size x 128 where each row is a kmeans centroid
            or visual word.
    -   step_size: same functionality as the stride in build_vocabulary(). Feel
            free to experiment with different values, but the rationale is that
            you may want to set it smaller than stride in build_vocabulary()
            such that you collect more features from the image.

    Returns:
    -   image_feats: N x k matrix, where k is the dimensionality of the
            feature representation. In this case, k will be equal to the number
            of clusters or equivalently the number of entries in each image's
            histogram (vocab_size) below.
    """
    # load vocabulary
    vocab = vocabulary

    vocab_size = len(vocab)
    num_images = len(image_arrays)

    feats = np.zeros((num_images, vocab_size))

    ###########################################################################
    # TODO: YOUR CODE HERE                                                    #
    ###########################################################################

    #1,2) for each training image, get SIFT descriptors
    #1,2) for each training image, get SIFT descriptors
    SIFT_descriptors = np.array([])
    for image in range(num_images):
        img = image_arrays[image]        
        #convert each input image to float32
        float_img = np.array(img, dtype='float32')
        
        #2) storing np array image as a tensor
        #should parameter be img_array?
        t = torch.from_numpy(float_img) 
        
        #reshape tensor
        #should parameters be image or img_array or image_arrays?
        img_tensor = t.reshape((1, 1, img.shape[0], img.shape[1])) 
        
        #get x and y coordinates for get_siftnet_features() function
        y, x = np.arange(10,img.shape[1]-10, step=step_size), np.arange(10,img.shape[0]-10, step=step_size)
        x,y = np.meshgrid(y,x)
        x = x.flatten()
        y = y.flatten()
        
        #get SIFT descriptors
        SIFT_descriptors = get_siftnet_features(img_tensor, x, y)
        quantize = kmeans_quantize(SIFT_descriptors,vocab)
        histogram,bins = np.histogram(quantize, bins=np.arange(vocab_size+1), density = True)
        feats[image, : ] = histogram


    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return feats
