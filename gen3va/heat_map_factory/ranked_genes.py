"""Prepares ranked genes for hierarchical clustering.
"""

import pandas

from gen3va.heat_map_factory import filters, utils


CLUSTERGRAMMER_URL = 'http://amp.pharm.mssm.edu/clustergrammer/vector_upload/'


def prepare_ranked_genes(diff_exp_method, signatures):
    """Prepares ranked genes for hierarchical clustering.
    """
    columns = []
    df = _get_raw_data(signatures)
    print(diff_exp_method)
    if diff_exp_method == 'z-score':
       print('using z-score')
       df = filters.filter_rows_by_variance(df)
    else:
        df = filters.filter_rows_by_highest_abs_val_mean(df)

    for col_name, signature in zip(df.columns, signatures):
        column = df.ix[:, col_name].tolist()
        column = [float(x) for x in column]
        genes = zip(df.index, column)

        data = [{'row_name': name, 'val': value} for name, value in genes]
        col = {
            'col_name': col_name,
            'data': data,
        }

        category_name = 'cell_type'
        opt = signature.get_optional_metadata(category_name)
        col['cat'] = opt.value.lower() if opt else ''
        columns.append(col)

    return columns


def _get_raw_data(signatures):
    """Creates a matrix of genes (rows) and signatures (columns).
    """
    df = pandas.DataFrame(index=[])
    for i, signature in enumerate(signatures):
        print('%s - %s' % (i, signature.extraction_id))

        ranked_genes = signature.combined_genes
        col_title = utils.column_title(i, signature)
        right = pandas.DataFrame(
            index=[rg.gene.name for rg in ranked_genes],
            columns=[col_title],
            data=[rg.value for rg in ranked_genes]
        )

        if type(right) is not pandas.DataFrame:
            continue

        df = df.join(right, how='outer')

        if not df.index.is_unique:
            df = df.groupby(df.index).mean()

    df = df.fillna(0)
    return df
