################################################################################
###########                   Sparse Topic Modeling                    #########
################################################################################
import numpy as np
import Sp_RecoverA
import Sp_Utils

def Sp_Top(X, anchor_group = None, C0 = 0.01, C1 = [1.1], cv_rep = 50):
  # Sparse topic model algorithm to recover for topic models: Estimate the topic number and anchor
  # words with its  partition (if not provided); Estimate the word-topic matrix A.
  #
  # Args: 
  #   X: p by n count data matrix (word - document).
  #   anchor_group: a list or an array of anchor words with its partition. When it is a one-dimension
  #      array or a one-dimension list, each element is considered as one anchor word for each topic.
  #      If anchor_group is None, use the Top algorithm to find anchor words with its partition.
  #   C0: a positive constant for estimating A (default is 0.01). 
  #   C1: a positive constant for finding anchor words (could be a grid for cross-validation)
  #   cv_rep: the number of repetitions by cross validation for selecting C1
  # 
  # Returns: 
  #   K: the number of topics.
  #   Anchor words: the set of anchor words
  #   Anchor groups: the partition of anchor words
  #   A: the estimated word-topic membership matrixx

  [p, n] = X.shape

  Ns = np.sum(X, 0).astype(float)
  P = max(n, p, max(Ns))
  X_freq = X / Ns
  new_X = p * X_freq.copy()                        # account for the scale of X
  D_X = np.sum(new_X, axis = 1)
  Sigma = Sp_Utils.GetSigma(new_X, Ns)
  R = (n ** 2) * Sigma / D_X[:,None] / D_X

  if anchor_group is None:
    
    if len(C1) > 1:
      optC1 = np.median([Sp_Tuning.CV_C1(new_X, Ns, C1) for i in range(cv_rep)])
    else:
      optC1 = C1[0]
    
    [eta, Q] = Sp_Utils.Obtain_eta_Q(Ns, new_X, D_X, Sigma)
    [rowMax, argRowMax] = [np.amax(R, axis = 1), np.argmax(R, axis = 1)]
    anchor_group = Sp_Anchor.SelectAnchor(R, optC1, rowMax, argRowMax, Q)


  K = len(anchor_group)
  if isinstance(anchor_group[0], int):
    anchor_group = [[anchor] for anchor in anchor_group]
  anchor_vec = [anchor for group in anchor_group for anchor in group]

  
  lbd = Sp_Utils.Cal_lbd(Ns, X_freq, D_X, P, K, anchor_vec)
  thresh = 7 * p * np.log(P) * np.sum(1 / Ns) / n
  
  A_hat = Sp_RecoverA.Est_A(D_X, R, anchor_group, anchor_vec, C0, lbd, thresh)
  
  return {"K": K, "Anchor words": [word for group in anchor_group for word in group], 
  "Anchor groups": anchor_group, "A": A_hat}



