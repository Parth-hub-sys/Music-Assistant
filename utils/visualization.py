from IPython.display import Image, display

def show_graph(graph):
    """Utility to display a LangGraph visualization in a notebook/IPython environment."""
    try:
        display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
    except Exception as e:
        print(f"Could not display graph: {e}")
        # Fallback to mermaid string
        print(graph.get_graph(xray=True).draw_mermaid())
