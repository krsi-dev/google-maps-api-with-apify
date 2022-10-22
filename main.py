import csv
import gooey 
import apify_client

"""
Main application with Gooey
to switch from CLI use --ignore-gooey
"""
@gooey.Gooey(
    # GUI setup
    program_name=f"google-maps-api-with-apify",
    required_cols=1,
    default_size=(400, 400),
)
def main():
    # Gooey parser
    parser = gooey.GooeyParser()

    # Required argument API key
    # key can be found in settings
    # integration tab in your APIFY profile
    # https://console.apify.com/account?tab=integrations
    parser.add_argument(
        "apify_key",
        help="APIFY key",
    )

    # Search query must include
    # category > sub category
    parser.add_argument(
        "search",
        type=str,
        help="example: coffee restaurant"
    )

    # Filter search query by city
    parser.add_argument(
        "city",
        type=str,
        help="example: pittsburgh"
    )

    # Define a maximum result to search
    parser.add_argument(
        "max_results",
        type=int,
        help="maximum results to search (sometimes apify increases the results)"
    )
    
    # Parse arguments
    args = parser.parse_args()

    # APIFY client
    client = apify_client.ApifyClient(args.apify_key)

    # Search query params
    run_input = {
        "maxImages": 0,
        "maxReviews": 0,
        "language": "en",
        "includeOpeningHours": True,
        "maxCrawledPlacesPerSearch": args.max_results,
        "proxyConfig": { "useApifyProxy": True },
        "searchStringsArray": args.search.split(),
    }

    print("Might take a while to finish ~ ")

    # Run the actor and wait for it to finish
    run = client.actor("drobnikj/crawler-google-places") \
        .call(run_input=run_input)

    # Open tsv file
    with open("main.tsv", "wt", newline='', encoding='utf-8') as csv_file:
        tsv_write = csv.writer(csv_file, delimiter="\t")

        # Write header
        tsv_write.writerow([
            "Name",
            "Address",
            "Opening Hours",
            "Phone Number",
            "Website"
        ])
        
        # Write results
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():

            # Skip business if permanently closed
            if item.get("permanentlyClosed"):
                continue

            # not all businesses list their opening hours
            open_hours = item.get("openingHours")
            if open_hours:
                open_hours = "\n".join([f'{x["day"]} {x["hours"]}' \
                    for x in open_hours])
            
            # address breakdown
            address = " ".join([
                item.get("street") or " ",
                item.get("city") or " ",
                item.get("state") or " "
            ]).strip()

            # finally write the details
            tsv_write.writerow([
                item.get("title"),
                address,
                open_hours,
                item.get("phone"),
                item.get("website")
            ])


if __name__ == "__main__":
    main()