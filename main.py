import argparse
import os
from dotenv import load_dotenv, set_key
import shutil

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

    my_parser.add_argument('-o',
                        metavar='--outputFilePath',
                        type=str,
                        help='Specify the Output filepath if you want to customice it',
                        required=False)


    # Execute the parse_args() method
    args = my_parser.parse_args()
    print(args)

    return args

def load_html_file(path: str):
    with open(path, encoding="utf-8") as fav_page:
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

def save_soup_to_html_file(soup, path: str):
    with open(path, "w", encoding="utf-8") as outf:
        outf.write(str(soup))

def find_all_current_groups(soup):
    existing_groups_html = soup.find_all("h2")
    existing_groups = []
    for group_html in existing_groups_html:
        existing_groups.append(group_html.string)
    return existing_groups

def perform_action(path_read: str, path_write: str, args):
    soup = load_html_file(path=path_read)

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

    save_soup_to_html_file(soup=soup, path=path_write)

def main():
    load_dotenv()
    args = parse_cli_arguments()

    FAVORITESLINKPAGE_DEFAULT_PATH = os.getenv("FAVORITESLINKPAGE_DEFAULT_PATH").strip()
    FAVORITESLINKPAGE_CUSTOM_PATH = os.getenv("FAVORITESLINKPAGE_CUSTOM_PATH").strip()

    # Fälle:
    # - kein -o, noch nie -o
    # - kein -o, aber früher schon mal
    # - erste Verwendung
    # - Verwendung mit gleichem Pfad
    # - Verwendung mit neuem Pfad

    # -o ist not used now and was never used
    if (args.o is None) and (len(FAVORITESLINKPAGE_CUSTOM_PATH) == 0):
        perform_action(path_read=FAVORITESLINKPAGE_DEFAULT_PATH,
                    path_write=FAVORITESLINKPAGE_DEFAULT_PATH,
                    args=args)
        return

    # no -o now but from earlier runs
    if (args.o is None) and (len(FAVORITESLINKPAGE_CUSTOM_PATH) > 0):
        perform_action(path_read=FAVORITESLINKPAGE_CUSTOM_PATH,
                    path_write=FAVORITESLINKPAGE_CUSTOM_PATH,
                    args=args)
        return

    # First use of -o
    if (args.o is not None) and (len(FAVORITESLINKPAGE_CUSTOM_PATH) == 0):
        # set CUSTOM_PATH in env file
        FAVORITESLINKPAGE_CUSTOM_PATH = args.o.strip()
        set_key(dotenv_path=".env", key_to_set="FAVORITESLINKPAGE_CUSTOM_PATH", value_to_set=FAVORITESLINKPAGE_CUSTOM_PATH)

        # copy and rename template to new location
        shutil.copy2(src="./favorites_page_template.html", dst=FAVORITESLINKPAGE_CUSTOM_PATH)
        perform_action(path_read=FAVORITESLINKPAGE_CUSTOM_PATH,
                    path_write=FAVORITESLINKPAGE_CUSTOM_PATH,
                    args=args)
        return

    # Use of -o with equal path as stored
    if (args.o is not None) and (args.o.strip() == FAVORITESLINKPAGE_CUSTOM_PATH):
        perform_action(path_read=FAVORITESLINKPAGE_CUSTOM_PATH,
                    path_write=FAVORITESLINKPAGE_CUSTOM_PATH,
                    args=args)
        return

    # Use of -o with different path as stored
    if (args.o is not None) and (args.o.strip() != FAVORITESLINKPAGE_CUSTOM_PATH):
        FAVORITESLINKPAGE_CUSTOM_PATH = args.o.strip()
        set_key(dotenv_path=".env", key_to_set="FAVORITESLINKPAGE_CUSTOM_PATH", value_to_set=FAVORITESLINKPAGE_CUSTOM_PATH)

        # check if file does not already exists
        if os.path.isfile(FAVORITESLINKPAGE_CUSTOM_PATH) == False:
            shutil.copy2(src="./favorites_page_template.html", dst=FAVORITESLINKPAGE_CUSTOM_PATH)

        perform_action(path_read=FAVORITESLINKPAGE_CUSTOM_PATH,
                    path_write=FAVORITESLINKPAGE_CUSTOM_PATH,
                    args=args)  
        return


if __name__ == "__main__":
    main()
