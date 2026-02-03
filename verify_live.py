from google_search_lib import google_search
import time

def verify_live():
    print("Attempting live search for 'python'...")
    try:
        results = google_search("python", num_results=5)

        if not results:
            print("No results found. (Likely blocked or parsing failed)")
        else:
            print(f"Success! Found {len(results)} results.")
            for i, res in enumerate(results):
                print(f"Result {i+1}: {res['title']}")
                print(f"  Link: {res['link']}")
                # print(f"  Snippet: {res['snippet'][:50]}...")

    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    verify_live()
