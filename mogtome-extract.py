import argparse
import urllib.request
from urllib.parse import urlparse
import csv

# External package imports
from bs4 import BeautifulSoup

# HTML tags and tag properties that uniquely define the data to look for
ITEM_LIST_IDENTIFIER    = {"class": "item__list__name"}
ITEM_COST_IDENTIFIER    = "td"

parser = argparse.ArgumentParser(description='Downloads Irregular Tomestone event rewards and writes them to a CSV file.')
parser.add_argument("-u", "--url", type=str, required=True, help="URL to a 'mogmog-collection' page on the FFXIV Lodestone.")
parser.add_argument("-o", "--output-file", type=str, default="output.csv", help="CSV file in the script's directory to write results to. Will be created if it doesn't exist.")
parser.add_argument("-v", "--verbose", action="store_true", help="If provided, prints out each tome reward to the console.")


def sanitize_url(s):
    parts = urlparse(s)
    if not parts.netloc.endswith("finalfantasyxiv.com"):
        raise ValueError(f"URL must belong to the domain 'finalfantasyxiv.com'\nGot: '{parts.netloc}' (via {s})")
    return s

def sanitize_csv_file_name(s):
    if len(s) > 4 and s[-4:] == ".csv":
        return s
    raise NameError(f"Output filename must end in '.csv'\nGot: '{s}'")

def get_cmd_line_inputs(inp: argparse.Namespace) -> tuple[str, bool, str]:
    url = sanitize_url(inp.url)
    output_filename = sanitize_csv_file_name(inp.output_file)
    verbose = inp.verbose
    return (url, output_filename, verbose)

################################

if __name__ == "__main__":
    print(">> Initializing....")

    URL,OUTPUT_FILENAME,VERBOSE = get_cmd_line_inputs(parser.parse_args())
    print(f"URL:            {URL}")
    print(f"Output file:    {OUTPUT_FILENAME}")
    print(f"Verbose output: {VERBOSE}")
    print()
    print("Working....")

    fp = urllib.request.urlopen(URL)
    soup = BeautifulSoup(fp, "html.parser")
    fp.close()

    title = soup.title.text
    print()
    print(title)

    info = ""
    try:
        info = soup.find_all('meta')[1]['content']
        print(info)
    except:
        print(">> Could not fetch event description")

    print()

    items = soup.find_all(attrs=ITEM_LIST_IDENTIFIER)
    costs = soup.find_all(ITEM_COST_IDENTIFIER)
    assert len(items) == len(costs)

    result = []
    for i,c in zip(items, costs):
        result.append((i.text, c.text))
        if VERBOSE:
            print(f"{i.text} (Cost: {c.text})")

    print()
    print(">> Got", len(result), "items")

    print(">> Writing to", OUTPUT_FILENAME)
    if len(result) > 0:
        with open(OUTPUT_FILENAME, "w+", newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([URL])
            csv_writer.writerow([title])
            csv_writer.writerow([info])
            for i in result:
                csv_writer.writerow(i)
        print(">> Done!")
    else:
        print(">> CSV failed to write (parsed no data)")
