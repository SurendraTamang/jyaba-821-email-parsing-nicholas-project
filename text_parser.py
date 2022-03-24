from utils import parse
import re
from datetime import datetime


def parser_text(data):
    res = {}
    regexes = {
        'Series': r"(?=Series.*?(\w+))",
        'Location': r"(?<=, a\s).*(?=-based)",
        'Location_': r"(?<=, a\s).*(?=-founded)",
        'Amount': r"\$\d+\s\w+",
        'Description': r"(?<=-based\s).*?(?=,)",
        'Description_': r"(?<=-founded\s).*?(?=,)"
    }

    res['name'] = data['Company']
    res['link'] = data['Company Url']
    res['updated_date'] = datetime.now()
    res['email_date'] = ""  # should be given

    # series
    series = re.findall(regexes['Series'], data['Text'])
    if series:
        res['series'] = series[0]
    else:
        res['series'] = ""

    # location
    location = re.findall(regexes['Location'], data['Text']) + \
        re.findall(regexes['Location_'], data['Text'])
    if location:
        res['location'] = location[0]
    else:
        res['location'] = ""

    # amount
    amount = re.findall(regexes['Amount'], data['Text'])
    if amount:
        res['Amount'] = amount[0]
    else:
        res['Amount'] = ""

    # description
    description = re.findall(regexes['Description'], data['Text']) + \
        re.findall(regexes['Description_'], data['Text'])
    if description:
        res['Description'] = description[0]
    else:
        res['Description'] = ""

    # investors
    investors = re.findall('(?i)investors including ([^.]+)', data['Text']) + re.findall(
        '(?i)investors include ([^.]+)', data['Text'])
    if investors:
        investors = investors[0].split(",")
        # last splitted item might have " and " so removing
        for i in range(len(investors)):
            if i == len(investors) - 1:
                if "and" in investors[i]:
                    res[f'investor{i}'] = investors[i].split(" and ")[1]
                else:
                    res[f'investor{i}'] = investors[i]
            else:
                res[f'investor{i}'] = investors[i]

    res['full text'] = data['Text']
    return res


def helper_parser(results):
    all_datas = []
    for key in list(results.keys()):
        key_data = results[key]
        for i in range(len(key_data)):
            all_datas.append(parser_text(key_data[i]))
    return all_datas


def main():
    # url
    url = "https://links.newsletter.fortune.com/u/click?_t=5c2d888702774d17aa3d0350287b6d73&_m=b82eca30bb3d4a18bd067b8b16563d7d&_e=zSjE-3sBaOj2qO3uri7ety6gfRgaw8yhX4EP0WxCGEIf9cHoknoS_A_gLzmNI3Flw7j3Knr45Ppypbfs-wUgumC2qE08-C23cISCJztr8qKXGEqmFwprgwpAmx5NhLiwWLLp_2dGi50nxnwj6LhwXZwwKcuG3IXQgZFo7g0qTi6JtM1OCljnXH2DZWsbsEWkYvaPb82qSdayCdSpDj2yfh038l0QMNnD7CnZBYfWL5vA58bI5vpGqWCZH2jFxefsxIMz3YK-683oCAHETXSukPF2y49MPO4CXQdMjpds6i6kOOdNtklosPFJfJ25BeGeZeTHovr6Q5gY1z3vvKjWt0O-XzlSPdt-VtafCXs8bm0lmCyKjjUfAPw9YEGY0V3L"
    results = parse(url)
    datas = helper_parser(results)
    print(datas)


if __name__ == "__main__":
    main()
