# get all author links from http://lists.ofono.org/pipermail/ofono/
# on each linked page, iterate through the list and count the number of times
# an author is mentioned
# track month, author name, and message count
from zc.testbrowser.browser import Browser
from BeautifulSoup import BeautifulSoup


def get_links(browser, match=""):
    results = []
    links = browser.mech_browser.links()
    for link in links:
        if not match:
            results.append(link)
        elif link.text == match:
            results.append(link)
    return results


def get_authors(browser):
    data = []
    for author_link in get_links(browser, match="[ Author ]"):
        url = author_link.base_url + author_link.url
        date = author_link.url.split("/")[0]
        browser.open(url)
        soup = BeautifulSoup(browser.contents)
        last_author = ""
        count = 0
        for li in soup.findAll("li"):
            author_data = li.find("i")
            if author_data:
                author = author_data.contents[0].strip()
                if author == last_author:
                    count += 1
                else:
                    data.append((date, last_author, str(count)))
                    count = 1
                last_author = author
        data.append((date, last_author, str(count)))
    return data


def print_csv(author_data):
    print '"Date", "Author", "Count"'
    for line in author_data:
        print '"%s"' % '", "'.join(line)


if __name__ == "__main__":
    browser = Browser("http://lists.ofono.org/pipermail/ofono/")
    authors = get_authors(browser)
    print_csv(authors)
