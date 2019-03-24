import urllib
from multiprocessing.pool import ThreadPool
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen


def check_link_status(link):
    """

    :param link: URL  string to be checked
    :return: boolean  reflecting link state
    """
    try:
        req = urllib.request.Request(url=link)
        resp = urllib.request.urlopen(req, timeout=4)
        print(f"checking link.... {link} status : {resp.status}")

    except Exception as e:
        print(f"PROBLEM WITH LINK  -->{e}")
        return False, link
    else:
        return True, link


def create_unique_links_set():
    """

    :return: collection of UNIQUE links located in page object
    """
    # request = Request("https://www.guardicore.com/")
    request = Request("https://www.youporn.com/")
    # test website , guardicore was having SSL issues this morning
    page_content = urlopen(request)
    soup = BeautifulSoup(page_content, features="html.parser")
    links = set()

    for ix, link_tag in enumerate(soup.find_all('a', href=True)):
        if "http" in link_tag['href']:
            print(f"DEBUG : link is {link_tag['href']} count : {ix}")
            links.add(link_tag['href'])

    return links


def create_links_list():
    """

    :return: collection of ALL links located in page object
    """
    request = Request("https://www.guardicore.com/")
    page_content = urlopen(request)
    soup = BeautifulSoup(page_content, features="html.parser")
    links = []

    for ix, link_tag in enumerate(soup.find_all('a', href=True)):
        if "http" in link_tag['href']:
            # print(f"link is {link_tag['href']} count : {ix}")
            links.append(link_tag['href'])

    return links


def execute_checker_parallel(links):
    good_links_set = set()
    bad_links_set = set()

    p = ThreadPool(processes=4)

    def my_callback(*result):

        good, link = result[0]
        # unpacking to avoid tuple in tuple issue with ThreadPool argument

        if good:
            good_links_set.add(link)
        else:
            bad_links_set.add(link)

    for link in links:
        p.apply_async(check_link_status, args=(link,), callback=my_callback)

    return good_links_set, bad_links_set


def execute_checker_non_parallel(links):
    good_links_set = set()
    bad_links_set = set()

    for link in links:
        if check_link_status(link):
            good_links_set.add(link)
        else:
            bad_links_set.add(link)
    return good_links_set, bad_links_set


def main():
    link_set = create_unique_links_set()
    # test_link_set = ('http://google.com', 'http://youtube.com')

    # gl, bl = execute_checker_parallel(link_set)
    gl, bl = execute_checker_non_parallel(link_set)

    print(f"{len(gl)} <---unique good links ,unique bad links --->{len(bl)}")

    with open('bad_links.txt', 'w') as f:
        for l in bl:
            f.writelines(l + "\n")


if __name__ == '__main__':
    main()
