import argparse
import sys

import bs4

def parse_cli_arguments():
    # Create the parser
    my_parser = argparse.ArgumentParser(description='Add Link to the favorites link page')

    # Add the arguments
    my_parser.add_argument('-g',
                        metavar='--group',
                        type=str,
                        help='The group the link should be added to.',
                        required=True)
                        
    my_parser.add_argument('-n',
                        metavar='--name',
                        type=str,
                        help='The name displayed for the link.',
                        required=True)

    my_parser.add_argument('-a',
                        metavar='--link',
                        type=str,
                        help='The full link to the page.',
                        required=True)
    
    my_parser.add_argument('-l',
                        help='Flag, if present it lists all groups currently present in the html file.',
                        action='store_true')


    # Execute the parse_args() method
    args = my_parser.parse_args()
    print(args)

    return args

def load_html_file():
    with open("favorites_page.html") as fav_page:
        txt = fav_page.read()
        soup = bs4.BeautifulSoup(txt, features="html.parser")    
    return soup

def find_group_in_soup(group: str, soup):
    return soup.find("h2", string=group)

def create_group_if_not_exists(group: str, soup):
    print("group does not exist")
    
    # new div for the new group
    new_div_group_tag = soup.new_tag("div", **{'class':'column floatingCol'})

    new_h2_group_tag = soup.new_tag("h2")
    new_h2_group_tag.append(group)
    new_div_group_tag.append(new_h2_group_tag)

    # insert new group after all existing groups
    existing_groups = soup.find_all("div", {"class": "column floatingCol"})
    
    if len(existing_groups) == 0:
        soup.body.div.append(new_div_group_tag)
    else:
        existing_groups[-1].insert_after(new_div_group_tag)

def create_new_favorite_a_tag(link: str, name: str, soup):
    new_a_tag = soup.new_tag("a", href=link, target="_blank")
    new_a_tag.append(name)
    return new_a_tag

def save_soup_to_html_file(soup):
    with open("favorites_page.html", "w") as outf:
        outf.write(str(soup))

def find_all_current_groups(soup):
    existing_groups_html = soup.find_all("h2")
    existing_groups = []
    for group_html in existing_groups_html:
        existing_groups.append(group_html.string)
    return existing_groups

def main():
    args = parse_cli_arguments()

    soup = load_html_file()

    # is the -l flag set?
    if args.l == True:
        print("\nThese groups are already present in the html file:")
        groups = find_all_current_groups(soup=soup)
        for group in groups:
            print(f"\t{group}")

    original_found_tag = find_group_in_soup(group=args.g, soup=soup)

    if original_found_tag is None:
        create_group_if_not_exists(group=args.g, soup=soup)
        original_found_tag = find_group_in_soup(group=args.g, soup=soup)

    new_a_tag = create_new_favorite_a_tag(link=args.a, name=args.n, soup=soup)

    # append a tag to existing soup
    original_found_tag.insert_after(new_a_tag)

    save_soup_to_html_file(soup=soup)

if __name__ == "__main__":
    main()
