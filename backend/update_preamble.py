from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["legalconnect"]
collection = db["constitution_parts"]

def update_preamble():
    correct_text = """WE, THE PEOPLE OF INDIA, having solemnly resolved to constitute India into a SOVEREIGN SOCIALIST SECULAR DEMOCRATIC REPUBLIC and to secure to all its citizens:

JUSTICE, social, economic and political;

LIBERTY of thought, expression, belief, faith and worship;

EQUALITY of status and of opportunity; and to promote among them all

FRATERNITY assuring the dignity of the individual and the unity and integrity of the Nation;

IN OUR CONSTITUENT ASSEMBLY this twenty-sixth day of November, 1949, do HEREBY ADOPT, ENACT AND GIVE TO OURSELVES THIS CONSTITUTION."""

    # Update using arrayFilters to target the specific article within the parts
    # Finding the part that contains the article with id "PREAMBLE"
    # And updating that specific article's content
    
    result = collection.update_one(
        {"articles.id": "PREAMBLE"},
        {"$set": {"articles.$[elem].content": correct_text}},
        array_filters=[{"elem.id": "PREAMBLE"}]
    )
    
    if result.modified_count > 0:
        print("Successfully updated Preamble content.")
    else:
        print("No document updated. Preamble might not exist or content is already same.")
        # Fallback: Check if matched
        if result.matched_count > 0:
            print("(Found document but no changes made)")
        else:
            print("ERROR: Could not find Preamble document to update.")

if __name__ == "__main__":
    update_preamble()
