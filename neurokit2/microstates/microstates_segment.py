# -*- coding: utf-8 -*-
import numpy as np

from ..stats import cluster
from ..stats.cluster_quality import _cluster_quality_gev
from .microstates_classify import microstates_classify
from .microstates_clean import microstates_clean


def microstates_segment(
    eeg,
    n_microstates=4,
    train="gfp",
    method="kmod",
    gfp_method="l1",
    sampling_rate=None,
    standardize_eeg=False,
    n_runs=10,
    max_iterations=1000,
    criterion="gev",
    random_state=None,
    optimize=False,
    **kwargs
):
    """**Segment M/EEG signal into Microstates**

    This functions identifies and extracts the microstates from an M/EEG signal using different
    clustering algorithms. Several runs of the clustering algorithm are performed, using different
    random initializations.The run that resulted in the best segmentation, as measured by global
    explained variance (GEV), is used.

    * **kmod**: Modified k-means algorithm.
    * **kmeans**: Normal k-means.
    * **kmedoids**: k-medoids clustering, a more stable version of k-means.
    * **pca**: Principal Component Analysis.
    * **ica**: Independent Component Analysis.
    * **aahc**: Atomize and Agglomerate Hierarchical Clustering. More computationally heavy.

    The microstates clustering is typically fitted on the EEG data at the global field power (GFP)
    peaks to maximize the signal to noise ratio and focus on moments of high global neuronal
    synchronization. It is assumed that the topography around a GFP peak remains stable and is at
    its highest signal-to-noise ratio at the GFP peak.

    Parameters
    ----------
    eeg : np.ndarray
        An array (channels, times) of M/EEG data or a Raw or Epochs object from MNE.
    n_microstates : int
        The number of unique microstates to find. Defaults to 4.
    train : Union[str, int, float]
        Method for selecting the timepoints how which to train the clustering algorithm. Can be
        'gfp' to use the peaks found in the Peaks in the global field power. Can be 'all', in which
        case it will select all the datapoints. It can also be a number or a ratio, in which case
        it will select the corresponding number of evenly spread data points. For instance,
        ``train=10`` will select 10 equally spaced datapoints, whereas ``train=0.5`` will select
        half the data. See ``microstates_peaks()``.
    method : str
        The algorithm for clustering. Can be one of ``"kmod"`` (default), ``"kmeans"``,
        ``"kmedoids"``, ``"pca"``, ``"ica"``, or ``"aahc"``.
    gfp_method : str
        The GFP extraction method, can be either ``"l1"`` (default) or ``"l2"`` to use the L1 or L2
        norm. See :func:`nk.eeg_gfp` for more details.
    sampling_rate : int
        The sampling frequency of the signal (in Hz, i.e., samples/second).
    standardize_eeg : bool
        Standardized (z-score) the data across time prior to GFP extraction
        using ``nk.standardize()``.
    n_runs : int
        The number of random initializations to use for the k-means algorithm.
        The best fitting segmentation across all initializations is used.
        Defaults to 10.
    max_iterations : int
        The maximum number of iterations to perform in the k-means algorithm.
        Defaults to 1000.
    criterion : str
        Which criterion to use to choose the best run for modified k-means algorithm,
        can be ``"gev"`` (default) which selects
        the best run based on the highest global explained variance, or ``"cv"`` which selects the
        best run based on the lowest cross-validation criterion. See ``nk.microstates_gev()``
        and ``nk.microstates_crossvalidation()`` for more details respectively.
    random_state : Union[int, numpy.random.RandomState]
        The seed or ``RandomState`` for the random number generator. Defaults
        to ``None``, in which case a different seed is chosen each time this
        function is called.
    optimize : bool
        To use a new optimized method in https://www.biorxiv.org/content/10.1101/289850v1.full.pdf.
        For the k-means modified method. Default to False.

    Returns
    -------
    dict
        Contains information about the segmented microstates:

        * **Microstates**: The topographic maps of the found unique microstates which has a shape of
          n_channels x n_states
        * **Sequence**: For each sample, the index of the microstate to which the sample has been
          assigned.
        * **GEV**: The global explained variance of the microstates.
        * **GFP**: The global field power of the data.
        * **Cross-Validation Criterion**: The cross-validation value of the iteration.
        * **Explained Variance**: The explained variance of each cluster map generated by PCA.
        * **Total Explained Variance**: The total explained variance of the cluster maps generated
          by PCA.

    Examples
    ---------
    * **Example 1**: k-means Algorithm

    .. ipython:: python

      import neurokit2 as nk

      # Download data
      eeg = nk.mne_data("filt-0-40_raw")
      # Average rereference and band-pass filtering
      eeg = nk.eeg_rereference(eeg, 'average').filter(1, 30, verbose=False)

      # Cluster microstates
      microstates = nk.microstates_segment(eeg, method="kmeans")
      @savefig p_microstate_segment1.png scale=100%
      nk.microstates_plot(microstates , epoch=(500, 750))
      @suppress
      plt.close()

      # Modified kmeans (currently comment out due to memory error)
      #out_kmod = nk.microstates_segment(eeg, method='kmod')
      # nk.microstates_plot(out_kmod, gfp=out_kmod["GFP"][0:500])

      # K-medoids (currently comment out due to memory error)
      #out_kmedoids = nk.microstates_segment(eeg, method='kmedoids')
      #nk.microstates_plot(out_kmedoids, gfp=out_kmedoids["GFP"][0:500])

    * **Example with PCA**

    .. ipython:: python

      out_pca = nk.microstates_segment(eeg, method='pca', standardize_eeg=True)
      @savefig p_microstate_segment2.png scale = 100%
      nk.microstates_plot(out_pca, gfp=out_pca["GFP"][0:500])
      @suppress
      plt.close()

    * **Example with ICA**

    .. ipython:: python

      out_ica = nk.microstates_segment(eeg, method='ica', standardize_eeg=True)
      @savefig p_microstate_segment3.png scale = 100%
      nk.microstates_plot(out_ica, gfp=out_ica["GFP"][0:500])
      @suppress
      plt.close()

    * **Example with AAHC**

    .. ipython:: python

      out_aahc = nk.microstates_segment(eeg, method='aahc')
      @savefig p_microstate_segment4.png scale = 100%
      nk.microstates_plot(out_aahc, gfp=out_aahc["GFP"][0:500])
      @suppress
      plt.close()


    See Also
    --------
    eeg_gfp, microstates_peaks, microstates_gev, microstates_crossvalidation, microstates_classify

    References
    ----------
    * Pascual-Marqui, R. D., Michel, C. M., & Lehmann, D. (1995). Segmentation of brain
      electrical activity into microstates: model estimation and validation. IEEE Transactions
      on Biomedical Engineering.

    """
    # Sanitize input
    data, indices, gfp, info_mne = microstates_clean(
        eeg,
        train=train,
        sampling_rate=sampling_rate,
        standardize_eeg=standardize_eeg,
        gfp_method=gfp_method,
        **kwargs
    )

    # Run clustering algorithm
    if method in ["kmods", "kmod", "kmeans modified", "modified kmeans"]:

        # If no random state specified, generate a random state
        if not isinstance(random_state, np.random.RandomState):
            random_state = np.random.RandomState(random_state)

        # Generate one random integer for each run
        random_state = random_state.choice(range(n_runs * 1000), n_runs, replace=False)

        # Initialize values
        gev = 0
        cv = np.inf
        microstates = None
        segmentation = None
        polarity = None
        info = None

        # Do several runs of the k-means algorithm, keep track of the best segmentation.
        for run in range(n_runs):

            # Run clustering on subset of data
            _, _, current_info = cluster(
                data[:, indices].T,
                method="kmod",
                n_clusters=n_microstates,
                random_state=random_state[run],
                max_iterations=max_iterations,
                threshold=1e-6,
                optimize=optimize,
            )
            current_microstates = current_info["clusters_normalized"]
            current_residual = current_info["residual"]

            # Run segmentation on the whole dataset
            s, p, g, g_all = _microstates_segment_runsegmentation(
                data, current_microstates, gfp, n_microstates=n_microstates
            )

            if criterion == "gev":
                # If better (i.e., higher GEV), keep this segmentation
                if g > gev:
                    microstates, segmentation, polarity, gev = (
                        current_microstates,
                        s,
                        p,
                        g,
                    )
                    gev_all = g_all
                    info = current_info
            elif criterion == "cv":
                # If better (i.e., lower CV), keep this segmentation
                # R2 and residual are proportional, use residual instead of R2
                if current_residual < cv:
                    microstates, segmentation, polarity = current_microstates, s, p
                    cv, gev, gev_all = current_residual, g, g_all
                    info -= current_info

    else:
        # Run clustering algorithm on subset
        _, microstates, info = cluster(
            data[:, indices].T,
            method=method,
            n_clusters=n_microstates,
            random_state=random_state,
            **kwargs
        )

        # Run segmentation on the whole dataset
        segmentation, polarity, gev, gev_all = _microstates_segment_runsegmentation(
            data, microstates, gfp, n_microstates=n_microstates
        )

    # Reorder
    segmentation, microstates = microstates_classify(segmentation, microstates)

    # CLustering quality
    #    quality = cluster_quality(data, segmentation, clusters=microstates, info=info, n_random=10, sd=gfp)

    # Output
    info = {
        "Microstates": microstates,
        "Sequence": segmentation,
        "GEV": gev,
        "GEV_per_microstate": gev_all,
        "GFP": gfp,
        "Polarity": polarity,
        "Info_algorithm": info,
        "Info": info_mne,
    }

    return info


# =============================================================================
# Utils
# =============================================================================
def _microstates_segment_runsegmentation(data, microstates, gfp, n_microstates):
    # Find microstate corresponding to each datapoint
    activation = microstates.dot(data)
    segmentation = np.argmax(np.abs(activation), axis=0)
    polarity = np.sign(np.choose(segmentation, activation))

    # Get Global Explained Variance (GEV)
    gev, gev_all = _cluster_quality_gev(
        data.T, microstates, segmentation, sd=gfp, n_clusters=n_microstates
    )
    return segmentation, polarity, gev, gev_all
