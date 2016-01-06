"""Computes principal component analysis.
"""

import pandas
import numpy as np
from sklearn import decomposition

from gen3va.db import db


def from_report(report):
    if report.report_type == 'default':
        return __from_gene_signatures(report.tag.gene_signatures)
    elif report.report_type == 'custom':
        return __from_gene_signatures(report.gene_signatures)


def from_extraction_ids(extraction_ids):
    gene_signatures = []
    for extraction_id in extraction_ids:
        gene_signature = db.get_gene_signature(extraction_id)
        gene_signatures.append(gene_signature)
    return __from_gene_signatures(gene_signatures)


def __from_gene_signatures(gene_signatures):
    data_frames = []
    for gene_signature in gene_signatures:

        # TODO: Fetch all gene signatures with a single DB query.
        genes = []
        values = []
        for rg in gene_signature.gene_lists[2].ranked_genes:
            genes.append(rg.gene.name)
            values.append([rg.value])

        # In principle, there should never be duplicates in our gene lists,
        # but an earlier version of GEO2Enrichr accidentally did not average
        # duplicates. Thus, any extraction ID for which this is the case will
        # fail if this step is not performed.
        indices, data = average_duplicates(np.array(genes), np.array(values))
        new_df = pandas.DataFrame(
            index=indices,
            data=[x[0] for x in data]
        )
        data_frames.append(new_df)

    df = pandas.concat(data_frames, axis=1)
    df = df.fillna(0)
    pca_coords, variance_explained = compute_pca(df.T)

    series = [{'name': 'Gene signatures', 'data': []}]
    for i, (x,y,z) in enumerate(pca_coords):
        key = gene_signatures[i].soft_file.dataset.title
        series[0]['data'].append({'x': x, 'y': y, 'z': z, 'name': key})

    pca_obj = {'series': series}

    # This is common with `from_soft_file`. Abstract it?
    max_vals = np.max(pca_coords, axis=0)
    min_vals = np.min(pca_coords, axis=0)
    ranges = np.vstack((max_vals*1.1, min_vals*1.1))
    pca_obj['ranges'] = ranges.tolist()

    titles = ['PC%s (%.2f' %
              (i, pct) + '%' + ' variance captured)' for i, pct in enumerate(variance_explained, start=1)]
    pca_obj['titles'] = titles

    return pca_obj


def compute_pca(df, max_components=3):
    """Performs principal component analysis and returns the first three
    principal components.
    """
    mat = df.as_matrix()
    pca = decomposition.PCA(n_components=None)

    # fit(X) - fit the model with X
    pca.fit(mat)

    # explained_variance_ratio_ - % of variance explained by each of the
    # selected components. Take only the first 3 components.
    variance_explained = pca.explained_variance_ratio_[0:max_components]
    variance_explained *= 100

    # transform(X) - apply the dimensionality reduction on X
    pca_coords = pca.transform(mat)[:, 0:max_components]

    # return the coordinates of the transformed data, plus the % of variance
    # explainced by each component
    return pca_coords, variance_explained


def average_duplicates(genes, values):
    """Finds duplicate genes and averages their expression data.
    """
    # See http://codereview.stackexchange.com/a/82020/59381 for details.
    folded, indices, counts = np.unique(genes, return_inverse=True, return_counts=True)
    output = np.zeros((folded.shape[0], values.shape[1]))
    np.add.at(output, indices, values)
    output /= counts[:, np.newaxis]
    return folded, output