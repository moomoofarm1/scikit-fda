import io
import math

import matplotlib.axes
import matplotlib.backends.backend_svg
import matplotlib.figure

import matplotlib.pyplot as plt


def _create_figure():
    """Create figure using the default backend."""
    fig = plt.figure()

    return fig


def _figure_to_svg(figure):
    """Return the SVG representation of a figure."""

    old_canvas = figure.canvas
    matplotlib.backends.backend_svg.FigureCanvas(figure)
    output = io.BytesIO()
    figure.savefig(output, format='svg')
    figure.set_canvas(old_canvas)
    data = output.getvalue()
    return data.decode('utf-8')


def _get_figure_and_axes(chart=None, fig=None, axes=None):
    """Obtain the figure and axes from the arguments."""

    num_defined = sum(e is not None for e in (chart, fig, axes))
    if num_defined > 1:
        raise ValueError("Only one of chart, fig and axes parameters"
                         "can be passed as an argument.")

    # Parse chart argument
    if chart is not None:
        if isinstance(chart, matplotlib.figure.Figure):
            fig = chart
        else:
            axes = chart

    if fig is None and axes is None:
        fig = fig = _create_figure()
        axes = []

    elif fig is not None:
        axes = fig.axes

    else:
        if isinstance(axes, matplotlib.axes.Axes):
            axes = [axes]

        fig = axes[0].figure

    return fig, axes


def _get_axes_shape(n_axes, n_rows=None, n_cols=None):
    """Get the number of rows and columns of the subplots"""

    if ((n_rows is not None and n_cols is not None)
            and ((n_rows * n_cols) < n_axes)):
        raise ValueError(f"The number of rows ({n_rows}) multiplied by "
                         f"the number of columns ({n_cols}) "
                         f"is less than the number of required "
                         f"axes ({n_axes})")

    if n_rows is None and n_cols is None:
        n_cols = int(math.ceil(math.sqrt(n_axes)))
        n_rows = int(math.ceil(n_axes / n_cols))
    elif n_rows is None and n_cols is not None:
        n_rows = int(math.ceil(n_axes / n_cols))
    elif n_cols is None and n_rows is not None:
        n_cols = int(math.ceil(n_axes / n_rows))

    return n_rows, n_cols


def _set_figure_layout(fig=None, axes=None,
                       dim=2, n_axes=1,
                       n_rows=None, n_cols=None):
    """Set the figure axes for plotting.

    Args:
        dim (int): dimension of the plot. Either 2 for a 2D plot or
            3 for a 3D plot.
        n_axes (int): Number of subplots.
        fig (figure object): figure over with the graphs are
            plotted in case ax is not specified.
        ax (list of axis objects): axis over where the graphs are
            plotted.
        n_rows (int, optional): designates the number of rows of the figure
            to plot the different dimensions of the image. Can only be passed
            if no axes are specified.
        n_cols (int, optional): designates the number of columns of the
            figure to plot the different dimensions of the image. Can only be
            passed if no axes are specified.

    Returns:
        (tuple): tuple containing:

            * fig (figure): figure object in which the graphs are plotted.
            * axes (list): axes in which the graphs are plotted.

    """
    if not (1 < dim < 4):
        raise NotImplementedError("Only bidimensional or tridimensional "
                                  "plots are supported.")

    if len(axes) != 0 and len(axes) != n_axes:
        raise ValueError(f"The number of axes must be 0 (to create them) or "
                         f"equal to the number of axes needed "
                         f"({n_axes} in this case).")

    if len(axes) != 0 and (n_rows is not None or n_cols is not None):
        raise ValueError("The number of columns and/or number of rows of "
                         "the figure, in which each dimension of the "
                         "image is plotted, can only be customized in case "
                         "that no axes are provided.")

    if dim == 2:
        projection = 'rectilinear'
    else:
        projection = '3d'

    if len(axes) == 0:
        # Create the axes

        n_rows, n_cols = _get_axes_shape(n_axes, n_rows, n_cols)
        fig.subplots(nrows=n_rows, ncols=n_cols,
                     subplot_kw={"projection": projection})
        axes = fig.axes

    else:
        # Check that the projections are right

        if not all(a.name == projection for a in axes):
            raise ValueError(f"The projection of the axes should be "
                             f"{projection}")

    return fig, axes


def _set_figure_layout_for_fdata(fdata, fig=None, axes=None,
                                 n_rows=None, n_cols=None):
    """Set the figure axes for plotting a
    :class:`~skfda.representation.FData` object.

    Args:
        fdata (FData): functional data object.
        fig (figure object): figure over with the graphs are
            plotted in case ax is not specified.
        ax (list of axis objects): axis over where the graphs are
            plotted.
        n_rows (int, optional): designates the number of rows of the figure
            to plot the different dimensions of the image. Can only be passed
            if no axes are specified.
        n_cols (int, optional): designates the number of columns of the
            figure to plot the different dimensions of the image. Can only be
            passed if no axes are specified.

    Returns:
        (tuple): tuple containing:

            * fig (figure): figure object in which the graphs are plotted.
            * axes (list): axes in which the graphs are plotted.

    """
    return _set_figure_layout(fig, axes,
                              dim=fdata.dim_domain + 1,
                              n_axes=fdata.dim_codomain,
                              n_rows=n_rows, n_cols=n_cols)


def _set_labels(fdata, fig=None, axes=None, patches=None):
    """Set labels if any.

    Args:
        fdata (FData): functional data object.
        fig (figure object): figure object containing the axes that
            implement set_xlabel and set_ylabel, and set_zlabel in case
            of a 3d projection.
        axes (list of axes): axes objects that implement set_xlabel and
            set_ylabel, and set_zlabel in case of a 3d projection; used if
            fig is None.
        patches (list of mpatches.Patch); objects used to generate each
            entry in the legend.

    """

    # Dataset name
    if fdata.dataset_label is not None:
        fig.suptitle(fdata.dataset_label)

    # Legend
    if patches is not None:
        fig.legend(handles=patches)
    elif patches is not None:
        axes[0].legend(handles=patches)

    # Axis labels
    if fdata.axes_labels is not None:
        if axes[0].name == '3d':
            for i in range(fdata.dim_codomain):
                if fdata.axes_labels[0] is not None:
                    axes[i].set_xlabel(fdata.axes_labels[0])
                if fdata.axes_labels[1] is not None:
                    axes[i].set_ylabel(fdata.axes_labels[1])
                if fdata.axes_labels[i + 2] is not None:
                    axes[i].set_zlabel(fdata.axes_labels[i + 2])
        else:
            for i in range(fdata.dim_codomain):
                if fdata.axes_labels[0] is not None:
                    axes[i].set_xlabel(fdata.axes_labels[0])
                if fdata.axes_labels[i + 1] is not None:
                    axes[i].set_ylabel(fdata.axes_labels[i + 1])
