import requests
import pandas as pd
import concurrent.futures
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

def search_business(search_term):
     data = requests.post(
        "https://firststop.sos.nd.gov/api/Records/businesssearch",
        headers={"authorization": "undefined"},
        json={
            "SEARCH_VALUE": search_term,
            "STARTS_WITH_YN": "false",
            "ACTIVE_ONLY_YN": True,
        },
    ).json()
     print(f"found {len(data['rows'])} | filtering companies starting from {search_term} ")
     return data

def get_business_details(business_id, business_name):
    details = requests.get(
        f"https://firststop.sos.nd.gov/api/FilingDetail/business/{business_id}/false",
        headers={"authorization": "undefined"},
    ).json()
    extracted_info = {
        "Company Name": business_name,
        "Owner Name": "",
        "Registered Agent": "",
        "Commercial Registered Agent": "",
    }
    for item in details.get("DRAWER_DETAIL_LIST", []):
        if item["LABEL"] in extracted_info:
            extracted_info[item["LABEL"]] = (
                item["VALUE"].split("\n")[0] if item["VALUE"] else ""
            )
    print(f"processed company: {business_name} ")
    return extracted_info

def visualize_graph(data_path):
    data = pd.read_csv(data_path)
    G = nx.Graph()
    for _, row in data.iterrows():
        G.add_node(row["Company Name"], type="company")
        for col, node_type in [
            ("Owner Name", "owner"),
            ("Registered Agent", "registered_agent"),
            ("Commercial Registered Agent", "commercial_agent"),
        ]:
            if pd.notna(row[col]):
                G.add_node(row[col], type=node_type)
                G.add_edge(row["Company Name"], row[col])
    pos = nx.spring_layout(G, scale=2)
    colors = [
        "blue"
        if G.nodes[n]["type"] == "company"
        else "magenta"
        if G.nodes[n]["type"] == "owner"
        else "red"
        if G.nodes[n]["type"] == "registered_agent"
        else "green"
        for n in G.nodes
    ]
    nx.draw(
        G,
        pos,
        node_size=50,
        node_color=colors,
        with_labels=False,
        font_size=8,
        alpha=0.8,
    )
    plt.title("Graph Visualization with Enhanced Connectivity")
    plt.show()

def process_and_save_business_details(search_term):
    search_results = search_business(search_term)
    filtered_companies = [
        (name, id)
        for id, data in search_results["rows"].items()
        for name in data["TITLE"]
        if name.lower().startswith(search_term.lower())
    ]
    print(f"filtered companies: {len(filtered_companies)}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        all_business_details = list(
            executor.map(lambda x: get_business_details(x[1], x[0]), filtered_companies)
        )
    output_file = f"Business_list_starting_with_{search_term}.csv"
    pd.DataFrame(all_business_details).to_csv(output_file, index=False)
    visualize_graph(output_file)

if __name__ == "__main__":
    process_and_save_business_details(input("Enter the search term: "))
