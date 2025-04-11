from dotenv import load_dotenv
from neo4j import GraphDatabase
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from pprint import pprint

load_dotenv()

def execute_neo4j_query(driver, query, parameters, db):
    with driver.session(database=db) as session:
        result = session.run(query, parameters)
    return result

def chapter_to_str(chapter):
    soup = BeautifulSoup(chapter.get_body_content(), 'html.parser')
    text = [para.get_text() for para in soup.find_all('p')]
    return text


def read_epub(path):
    book = epub.read_epub(path)
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    return items    

def main():
    
    # Connect to Neo4j
    neo4j_uri = os.environ.get("NEO4J_HOST")
    neo4j_user = os.environ.get("NEO4J_USER")
    neo4j_password = os.environ.get("NEO4J_PASSWORD")
    db = os.environ.get("NEO4J_DB")
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    items = read_epub('data/Murdoch,Iris_-TheSovereigntyofGood-Routledge(1970).epub')
    i = 0
    for item in items:
        if 'chapter' in item.get_name():
            # print(item.get_name())
            pars = chapter_to_str(item)
            for par in pars:
                i += 1
                query = "CREATE (t:TEXT {id: $id,text: $text})"
                params = {
                    "id":i,
                    "text":par
                }
                
                execute_neo4j_query(driver, query, params, db)
                if i % 100 == 0:
                    print(f"Done with {i}")

    #     print(item)
    
    driver.close()

if __name__ == "__main__":
    main()
