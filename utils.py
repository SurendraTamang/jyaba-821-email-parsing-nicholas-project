import requests
from lxml import html
from playwright.sync_api import sync_playwright


def parse(url):  # url needs to be https://links.newsletter.fortune.com format
    res = requests.get(url)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(res.url)
        tree = html.fromstring(page.content())
        browser.close()

    keys = tree.xpath(".//p[not(a)]/b/text()")
    temp = []
    datas = {}
    for i in range(len(keys) - 1, -1, -1):
        if temp == []:
            temp = tree.xpath(
                f"//p/b[text()='{keys[i]}']/../following-sibling::p/a/..")
            datas[keys[i]] = temp
        else:
            temp2 = tree.xpath(
                f"//p/b[text()='{keys[i]}']/../following-sibling::p/a/..")
            datas[keys[i]] = [ele for ele in temp2 if ele not in temp]
            temp = temp2

    categories = {}
    for d in keys:
        result = []
        for vd in datas[d]:
            row = {}
            row['Company'] = vd.xpath("./a//text()")[0]
            row['Company Url'] = vd.xpath("./a/@href")[0]
            row['Text'] = "".join(vd.xpath(".//text()"))
            result.append(row)
        categories[d] = result

    return categories


if __name__ == "__main__":
    print(parse("https://links.newsletter.fortune.com/u/click?_t=5c2d888702774d17aa3d0350287b6d73&_m=b82eca30bb3d4a18bd067b8b16563d7d&_e=zSjE-3sBaOj2qO3uri7ety6gfRgaw8yhX4EP0WxCGEIf9cHoknoS_A_gLzmNI3Flw7j3Knr45Ppypbfs-wUgumC2qE08-C23cISCJztr8qKXGEqmFwprgwpAmx5NhLiwWLLp_2dGi50nxnwj6LhwXZwwKcuG3IXQgZFo7g0qTi6JtM1OCljnXH2DZWsbsEWkYvaPb82qSdayCdSpDj2yfh038l0QMNnD7CnZBYfWL5vA58bI5vpGqWCZH2jFxefsxIMz3YK-683oCAHETXSukPF2y49MPO4CXQdMjpds6i6kOOdNtklosPFJfJ25BeGeZeTHovr6Q5gY1z3vvKjWt0O-XzlSPdt-VtafCXs8bm0lmCyKjjUfAPw9YEGY0V3L"))
