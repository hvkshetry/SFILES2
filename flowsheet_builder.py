import sys
import os
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# Avoid 'unicodeescape' issues by using raw strings or double backslashes
# for any local paths. If needed, you can do:
#
# python -m streamlit run "C:\\Users\\hvksh\\SFILES2\\flowsheet_builder.py"
# ---------------------------------------------------------------------

# Set page config at the very top
st.set_page_config(
    page_title="SFILES 2.0 Flowsheet Builder",
    page_icon="🏭",
    layout="wide",
)

# If SFILES2 is in a local folder, ensure we add it to sys.path
SFILES2_PATH = os.path.join(os.getcwd())
if SFILES2_PATH not in sys.path:
    sys.path.append(SFILES2_PATH)

# Attempt to load the official SFILES2 library
try:
    from Flowsheet_Class.flowsheet import Flowsheet as SFILES2_Flowsheet
    # We won't need to import nx_to_sfiles directly
    SFILES2_AVAILABLE = True
except ImportError:
    SFILES2_AVAILABLE = False

# ---------------------------------------------------------------------
# Helper: Generate SFILES from session-state (units + connections)
# using the official SFILES2_Flowsheet only
# ---------------------------------------------------------------------
def generate_sfiles_from_session_state():
    """
    Build an official SFILES2_Flowsheet from st.session_state units/connections,
    then call convert_to_sfiles(version='v2') to get the final SFILES string.
    """
    if not SFILES2_AVAILABLE:
        st.error("SFILES2 library not available. Cannot generate SFILES.")
        return ""

    # If no units, just return empty
    if not st.session_state.units:
        return ""

    fs = SFILES2_Flowsheet()
    try:
        # Add units
        for unit in st.session_state.units:
            fs.add_unit(unique_name=unit["name"])

        # Add connections
        for (source, target, tagstring) in st.session_state.connections:
            if isinstance(tagstring, str):
                parsed_tags = [t.strip() for t in tagstring.split(",") if t.strip()]
                tag_dict = {"he": [], "col": parsed_tags, "signal": []}
            else:
                tag_dict = {"he": [], "col": [], "signal": []}
            fs.add_stream(source, target, tags=tag_dict)

        # Convert to SFILES (v2)
        fs.convert_to_sfiles(version="v2")
        return fs.sfiles
    except Exception as e:
        st.error(f"Error generating SFILES: {e}")
        return ""

# ---------------------------------------------------------------------
# Helper: Parse SFILES -> store in session_state (units, connections)
# using the official library
# ---------------------------------------------------------------------
def parse_sfiles_to_session_state(sfiles_string):
    """
    Parse an SFILES v2 string with the official SFILES2_Flowsheet,
    then update st.session_state.units and st.session_state.connections.
    """
    if not SFILES2_AVAILABLE:
        st.error("SFILES2 library not available. Cannot parse SFILES.")
        return False

    if not sfiles_string.strip():
        st.warning("Empty SFILES string provided. Nothing to import.")
        return False

    try:
        fs = SFILES2_Flowsheet(sfiles_in=sfiles_string)
        # Wipe out old session data
        st.session_state.units = []
        st.session_state.connections = []

        # Collect units
        for node in fs.state.nodes():
            parts = node.split("-")
            unit_type = parts[0] if len(parts) > 1 else ""
            st.session_state.units.append({"name": node, "type": unit_type})

        # Collect edges
        for u, v, data in fs.state.edges(data=True):
            tags = ""
            if "tags" in data:
                tag_data = data["tags"]
                if isinstance(tag_data, dict) and "col" in tag_data:
                    # Convert list to CSV
                    tags_list = tag_data["col"]
                    if tags_list:
                        tags = ",".join(tags_list)
                elif isinstance(tag_data, str):
                    tags = tag_data

            st.session_state.connections.append((u, v, tags))

        return True
    except Exception as e:
        st.error(f"Error parsing SFILES: {e}")
        return False

# ---------------------------------------------------------------------
# Utility: get existing connections from session_state (for display)
# ---------------------------------------------------------------------
def get_existing_connections():
    conns = []
    if "connections" in st.session_state:
        for (f, t, tags) in st.session_state.connections:
            conns.append({"from": f, "to": t, "tags": tags})
    return conns

# ---------------------------------------------------------------------
# Utility: remove a connection by (from_unit, to_unit)
# ---------------------------------------------------------------------
def delete_connection(from_unit, to_unit):
    if "connections" in st.session_state:
        st.session_state.connections = [
            (f, t, tags)
            for (f, t, tags) in st.session_state.connections
            if not (f == from_unit and t == to_unit)
        ]
        # Recompute the SFILES
        st.session_state.sfiles_string = generate_sfiles_from_session_state()

# ---------------------------------------------------------------------
# Render the flowsheet as a graph (via NetworkX + matplotlib)
# purely from session_state
# ---------------------------------------------------------------------
def render_flowsheet_graph():
    G = nx.DiGraph()
    for unit in st.session_state.units:
        G.add_node(unit["name"])
    for (src, dst, raw_tags) in st.session_state.connections:
        if isinstance(raw_tags, str):
            parsed = [t.strip() for t in raw_tags.split(",") if t.strip()]
            tag_dict = {"he": [], "col": parsed, "signal": []}
        else:
            tag_dict = {"he": [], "col": [], "signal": []}
        G.add_edge(src, dst, tags=tag_dict)

    fig, ax = plt.subplots(figsize=(9, 5))
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=1500, ax=ax)
    nx.draw_networkx_labels(G, pos, font_weight="bold", ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color="gray", ax=ax)

    # Edge labels
    edge_labels = {}
    for (u, v, edata) in G.edges(data=True):
        if "tags" in edata and edata["tags"]:
            # Flatten out the tags
            col_tags = edata["tags"].get("col", [])
            # Could also look at edata["tags"]["he"] or ["signal"], if used
            all_tags = col_tags  # For brevity, just show col
            if all_tags:
                edge_labels[(u, v)] = ",".join(all_tags)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

    ax.set_title("Flowsheet Graph")
    plt.tight_layout()
    return fig

# ---------------------------------------------------------------------
# Functions that modify session_state (units + connections)
# ---------------------------------------------------------------------
def add_unit_to_session_state(unit_name, unit_type=""):
    if unit_type and "-" not in unit_name:
        final_name = f"{unit_type}-{unit_name}"
    else:
        final_name = unit_name
    st.session_state.units.append({"name": final_name, "type": unit_type})
    st.session_state.sfiles_string = generate_sfiles_from_session_state()

def add_stream_to_session_state(from_unit, to_unit, tags=""):
    st.session_state.connections.append((from_unit, to_unit, tags))
    st.session_state.sfiles_string = generate_sfiles_from_session_state()

def get_existing_units():
    return [u["name"] for u in st.session_state.units]

def create_branch_in_session_state(from_unit, to_units, tags_list=None):
    if tags_list is None:
        tags_list = ["" for _ in to_units]
    for i, tounit in enumerate(to_units):
        st.session_state.connections.append((from_unit, tounit, tags_list[i]))
    st.session_state.sfiles_string = generate_sfiles_from_session_state()

def create_join_in_session_state(from_units, to_unit, tags_list=None):
    if tags_list is None:
        tags_list = ["" for _ in from_units]
    for i, fromu in enumerate(from_units):
        st.session_state.connections.append((fromu, to_unit, tags_list[i]))
    st.session_state.sfiles_string = generate_sfiles_from_session_state()

def create_cycle_in_session_state(from_unit, to_unit, tags=""):
    st.session_state.connections.append((from_unit, to_unit, tags))
    st.session_state.sfiles_string = generate_sfiles_from_session_state()

# ---------------------------------------------------------------------
# Initialize session_state
# ---------------------------------------------------------------------
if "sfiles_string" not in st.session_state:
    st.session_state.sfiles_string = ""
if "form_key" not in st.session_state:
    st.session_state.form_key = 0
if "connections" not in st.session_state:
    st.session_state.connections = []
if "units" not in st.session_state:
    st.session_state.units = []
if "export_text" not in st.session_state:
    st.session_state.export_text = ""

# ---------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------
st.header("SFILES 2.0 Flowsheet Builder (Official Library)")

if not SFILES2_AVAILABLE:
    st.error("SFILES2 official library not found. Please install it (e.g. `pip install -e .`) and restart.")
    st.stop()

col1, col2 = st.columns([1, 2])

# --------------- COLUMN 1: Unit/Stream Management ---------------
with col1:
    st.subheader("Add a Unit")
    unit_type = st.text_input("Unit Type", key=f"unit_type_{st.session_state['form_key']}")
    unit_name = st.text_input("Unique Name", key=f"unit_name_{st.session_state['form_key']}")

    if st.button("Add Unit", key=f"add_unit_{st.session_state['form_key']}"):
        if unit_name.strip():
            add_unit_to_session_state(unit_name, unit_type)
            st.session_state["form_key"] += 1
            st.rerun()
        else:
            st.warning("Please provide a unique name for the unit.")

    # Manage Units
    st.subheader("Manage Units")
    if st.session_state.units:
        unit_list = [u["name"] for u in st.session_state.units]
        unit_to_manage = st.selectbox("Select Unit to Manage", unit_list, key=f"manage_unit_{st.session_state['form_key']}")
        if unit_to_manage:
            sel_unit = next((u for u in st.session_state.units if u["name"] == unit_to_manage), None)
            if sel_unit:
                colA, colB = st.columns(2)
                with colA:
                    if st.button("Delete Unit", key=f"delete_unit_{st.session_state['form_key']}"):
                        # Check if it is in any connections
                        used_in_conn = any(
                            from_ == unit_to_manage or to_ == unit_to_manage
                            for (from_, to_, _) in st.session_state.connections
                        )
                        if used_in_conn:
                            st.error("Cannot delete a unit that has existing connections. Remove them first.")
                        else:
                            st.session_state.units = [u for u in st.session_state.units if u["name"] != unit_to_manage]
                            st.session_state.sfiles_string = generate_sfiles_from_session_state()
                            st.session_state["form_key"] += 1
                            st.rerun()
                with colB:
                    new_type = st.text_input(
                        "Edit Unit Type",
                        value=sel_unit.get("type", ""),
                        key=f"edit_unit_type_{st.session_state['form_key']}"
                    )
                    if st.button("Update Type", key=f"update_type_{st.session_state['form_key']}"):
                        for u in st.session_state.units:
                            if u["name"] == unit_to_manage:
                                u["type"] = new_type
                        st.success(f"Updated type of {unit_to_manage} to {new_type}")
                        # Recompute SFILES
                        st.session_state.sfiles_string = generate_sfiles_from_session_state()
                        st.session_state["form_key"] += 1
                        st.rerun()

    else:
        st.info("No units added yet.")

    # Add Stream
    st.subheader("Add a Stream")
    existing_units = get_existing_units()
    if not existing_units:
        st.info("Add at least one unit first.")
    else:
        from_unit = st.selectbox("From Unit", existing_units, key=f"from_unit_{st.session_state['form_key']}")
        to_unit = st.selectbox("To Unit", existing_units, key=f"to_unit_{st.session_state['form_key']}")
        stream_tags = st.text_input("Tags (comma-separated)", key=f"stream_tags_{st.session_state['form_key']}")
        if st.button("Add Stream", key=f"add_stream_{st.session_state['form_key']}"):
            if from_unit == to_unit:
                st.warning("From and To cannot be the same.")
            else:
                add_stream_to_session_state(from_unit, to_unit, stream_tags)
                st.session_state["form_key"] += 1
                st.rerun()

    # Manage Connections
    if existing_units:
        st.subheader("Manage Connections")
        conns = get_existing_connections()
        if not conns:
            st.info("No connections yet.")
        else:
            st.write("Existing connections:")
            for i, c in enumerate(conns):
                colC = st.columns([3,3,3,1])
                with colC[0]:
                    st.text(f"From: {c['from']}")
                with colC[1]:
                    st.text(f"To: {c['to']}")
                with colC[2]:
                    st.text(f"Tags: {c['tags']}")
                with colC[3]:
                    if st.button("Delete", key=f"del_conn_{i}_{st.session_state['form_key']}"):
                        delete_connection(c["from"], c["to"])
                        st.session_state["form_key"] += 1
                        st.rerun()

    # Branch creation
    if len(existing_units) >= 2:
        st.subheader("Create Branch")
        bfrom = st.selectbox("Branch from Unit", existing_units, key=f"branch_from_{st.session_state['form_key']}")
        bcount = st.number_input("Number of branch outputs", min_value=2, max_value=5, value=2, step=1)
        b_units = []
        b_tags = []
        for i in range(int(bcount)):
            bc1, bc2 = st.columns(2)
            with bc1:
                bu = st.selectbox(f"To Unit {i+1}", existing_units, key=f"branch_to_{i}_{st.session_state['form_key']}")
                b_units.append(bu)
            with bc2:
                tg = st.text_input(f"Tags {i+1}", key=f"branch_tag_{i}_{st.session_state['form_key']}")
                b_tags.append(tg)
        if st.button("Create Branch", key=f"create_branch_{st.session_state['form_key']}"):
            create_branch_in_session_state(bfrom, b_units, b_tags)
            st.session_state["form_key"] += 1
            st.rerun()

    # Join creation
    if len(existing_units) >= 2:
        st.subheader("Create Join")
        jto = st.selectbox("Join to Unit", existing_units, key=f"join_to_{st.session_state['form_key']}")
        jcount = st.number_input("Number of join inputs", min_value=2, max_value=5, value=2, step=1)
        j_froms = []
        j_tags = []
        for i in range(int(jcount)):
            jc1, jc2 = st.columns(2)
            with jc1:
                ju = st.selectbox(f"From Unit {i+1}", existing_units, key=f"join_from_{i}_{st.session_state['form_key']}")
                j_froms.append(ju)
            with jc2:
                jt = st.text_input(f"Tags {i+1}", key=f"join_tag_{i}_{st.session_state['form_key']}")
                j_tags.append(jt)
        if st.button("Create Join", key=f"create_join_{st.session_state['form_key']}"):
            create_join_in_session_state(j_froms, jto, j_tags)
            st.session_state["form_key"] += 1
            st.rerun()

    # Cycle creation
    if len(existing_units) >= 2:
        st.subheader("Create Recycle")
        cyc_from = st.selectbox("Recycle from Unit", existing_units, key=f"recycle_from_{st.session_state['form_key']}")
        cyc_to = st.selectbox("Recycle to Unit", existing_units, key=f"recycle_to_{st.session_state['form_key']}")
        cyc_tags = st.text_input("Recycle Tags (comma-separated)", key=f"recycle_tags_{st.session_state['form_key']}")
        if st.button("Create Recycle", key=f"create_recycle_{st.session_state['form_key']}"):
            if cyc_from == cyc_to:
                st.warning("From/To cannot be the same.")
            else:
                create_cycle_in_session_state(cyc_from, cyc_to, cyc_tags)
                st.session_state["form_key"] += 1
                st.rerun()

# --------------- COLUMN 2: SFILES Output / Import-Export / Visualization ---------------
with col2:
    st.subheader("SFILES 2.0 String")
    st.text_area("SFILES Output", st.session_state.sfiles_string, height=100, disabled=True)

    # Import/Export
    st.subheader("Import/Export SFILES")
    import_box = st.text_area("Import SFILES", value=st.session_state.get("export_text", ""), height=100)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Import"):
            # Attempt to parse SFILES
            if import_box.strip():
                ok = parse_sfiles_to_session_state(import_box)
                if ok:
                    st.session_state.sfiles_string = import_box
                    st.success("Imported SFILES.")
                    st.session_state["form_key"] += 1
                    st.rerun()
                else:
                    st.error("Failed to parse SFILES.")
            else:
                st.warning("Nothing to import.")
    with c2:
        if st.button("Export to Text Area"):
            out_sfiles = generate_sfiles_from_session_state()
            st.session_state.export_text = out_sfiles
            st.session_state.sfiles_string = out_sfiles
            st.success("SFILES exported.")
            st.session_state["form_key"] += 1
            st.rerun()

    st.subheader("Flowsheet Visualization")
    if st.session_state.units:
        try:
            fig = render_flowsheet_graph()
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error rendering flowsheet: {e}")
    else:
        st.info("No flowsheet data yet. Add a unit to begin.")
