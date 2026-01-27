from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["legalconnect"]
collection = db["constitution_parts"]

missing_articles = {
    "43B": "The State shall endeavour to promote voluntary formation, autonomous functioning, democratic control and professional management of co-operative societies.",
    
    "124A": """(1) There shall be a Commission to be known as the National Judicial Appointments Commission consisting of the following persons, namely:—
(a) the Chief Justice of India as Chairperson, ex officio;
(b) two other senior Judges of the Supreme Court next to the Chief Justice of India, as Members ex officio;
(c) the Union Minister in charge of Law and Justice as ex officio Member;
(d) two eminent persons, as Members.
(2) The Chief Justice of India and the two other senior Judges of the Supreme Court next to the Chief Justice of India shall be nominated by the President in consultation with the Chief Justice of India and the two other senior Judges of the Supreme Court next to the Chief Justice of India.
(3) The eminent persons shall be nominated by a committee consisting of the Prime Minister, the Chief Justice of India and the Leader of Opposition in the House of the People or where there is no such Leader of Opposition, then, the Leader of the single largest Opposition Party in the House of the People:
Provided that out of the two eminent persons, one person shall be from amongst the persons belonging to the Scheduled Castes, Scheduled Tribes, Other Backward Classes, Minorities or Women:
Provided further that an eminent person shall be nominated for a period of three years and shall not be eligible for re-nomination.""",

    "124B": """It shall be the duty of the National Judicial Appointments Commission to—
(a) recommend persons for appointment as Chief Justice of India, Judges of the Supreme Court, Chief Justices of High Courts and other Judges of High Courts;
(b) recommend transfer of Chief Justices and other Judges from one High Court to any other High Court; and
(c) ensure that the person recommended is of ability and integrity.""",

    "279A": """(1) The President shall, within sixty days from the date of commencement of the Constitution (One Hundred and First Amendment) Act, 2016, by order, constitute a Council to be called the Goods and Services Tax Council.
(2) The Goods and Services Tax Council shall consist of the following members, namely:—
(a) the Union Finance Minister—Chairperson;
(b) the Union Minister of State in charge of Revenue or Finance—Member;
(c) the Minister in charge of Finance or Taxation or any other Minister nominated by each State Government—Members.
(3) The Members of the Goods and Services Tax Council referred to in sub-clause (c) of clause (2) shall, as soon as may be, choose one amongst themselves to be the Vice-Chairperson of the Council for such period as they may decide.
(4) The Goods and Services Tax Council shall make recommendations to the Union and the States on—
(a) the taxes, cesses and surcharges levied by the Union, the States and the local bodies which may be subsumed in the goods and services tax;
(b) the goods and services that may be subjected to, or exempted from, the goods and services tax;
(c) model Goods and Services Tax Laws, principles of levy, apportionment of Goods and Services Tax levied on supplies in the course of inter-State trade or commerce under article 269A and the principles that govern the place of supply;
(d) the threshold limit of turnover below which goods and services may be exempted from goods and services tax;
(e) the rates including floor rates with bands of goods and services tax;
(f) any special rate or rates for a specified period, to raise additional resources during any natural calamity or disaster;
(g) special provision with respect to the States of Arunachal Pradesh, Assam, Jammu and Kashmir, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, Tripura, Himachal Pradesh and Uttarakhand; and
(h) any other matter relating to the goods and services tax, as the Council may decide.
(5) The Goods and Services Tax Council shall recommend the date on which the goods and services tax be levied on petroleum crude, high speed diesel, motor spirit (commonly known as petrol), natural gas and aviation turbine fuel.
(6) While discharging the functions conferred by this article, the Goods and Services Tax Council shall be guided by the need for a harmonised structure of goods and services tax and for the development of a harmonised national market for goods and services.""",

    "320": """(1) It shall be the duty of the Union and the State Public Service Commissions to conduct examinations for appointments to the services of the Union and the services of the State respectively.
(2) It shall also be the duty of the Union Public Service Commission, if requested by any two or more States so to do, to assist those States in framing and operating schemes of joint recruitment for any services for which candidates possessing special qualifications are required.
(3) The Union Public Service Commission or the State Public Service Commission, as the case may be, shall be consulted—
(a) on all matters relating to methods of recruitment to civil services and for civil posts;
(b) on the principles to be followed in making appointments to civil services and posts and in making promotions and transfers from one service to another and on the suitability of candidates for such appointments, promotions or transfers;
(c) on all disciplinary matters affecting a person serving under the Government of India or the Government of a State in a civil capacity, including memorials or petitions relating to such matters;
(d) on any claim by or in respect of a person who is serving or has served under the Government of India or the Government of a State or under the Crown in India or under the Government of an Indian State, in a civil capacity, that any costs incurred by him in defending legal proceedings instituted against him in respect of acts done or purporting to be done in the execution of his duty should be paid out of the Consolidated Fund of India, or, as the case may be, out of the Consolidated Fund of the State;
(e) on any claim for the award of a pension in respect of injuries sustained by a person while serving under the Government of India or the Government of a State or under the Crown in India or under the Government of an Indian State, in a civil capacity, and any question as to the amount of any such award,
and it shall be the duty of a Public Service Commission to advise on any matter so referred to them and on any other matter which the President, or, as the case may be, the Governor of the State, may refer to them:
Provided that the President as respects the all-India services and also as respects other services and posts in connection with the affairs of the Union, and the Governor, as respects other services and posts in connection with the affairs of a State, may make regulations specifying the matters in which either generally, or in any particular class of case or in any particular circumstances, it shall not be necessary for a Public Service Commission to be consulted.
(4) Nothing in clause (3) shall require a Public Service Commission to be consulted as respects the manner in which any provision referred to in clause (4) of article 16 may be made or as respects the manner in which effect may be given to the provisions of article 335.
(5) All regulations made under the proviso to clause (3) by the President or the Governor of a State shall be laid for not less than fourteen days before each House of Parliament or the House or each House of the Legislature of the State, as the case may be, as soon as possible after they are made, and shall be subject to such modifications, whether by way of repeal or amendment, as both Houses of Parliament or the House or both Houses of the Legislature of the State may make during the session in which they are so laid.""",

    "338B": """(1) There shall be a Commission for the socially and educationally backward classes to be known as the National Commission for Backward Classes.
(2) Subject to the provisions of any law made in this behalf by Parliament, the Commission shall consist of a Chairperson, Vice-Chairperson and three other Members and the conditions of service and tenure of office of the Chairperson, Vice-Chairperson and other Members so appointed shall be such as the President may by rule determine.
(3) The Chairperson, Vice-Chairperson and other Members of the Commission shall be appointed by the President by warrant under his hand and seal.
(4) The Commission shall have the power to regulate its own procedure.
(5) It shall be the duty of the Commission—
(a) to investigate and monitor all matters relating to the safeguards provided for the socially and educationally backward classes under this Constitution or under any other law for the time being in force or under any order of the Government and to evaluate the working of such safeguards;
(b) to inquire into specific complaints with respect to the deprivation of rights and safeguards of the socially and educationally backward classes;
(c) to participate and advise on the socio-economic development of the socially and educationally backward classes and to evaluate the progress of their development under the Union and any State;
(d) to present to the President, annually and at such other times as the Commission may deem fit, reports upon the working of those safeguards;
(e) to make such reports containing recommendations as to the measures that should be taken by the Union or any State for the effective implementation of those safeguards and other measures for the protection, welfare and socio-economic development of the socially and educationally backward classes; and
(f) to discharge such other functions in relation to the protection, welfare and development and advancement of the socially and educationally backward classes as the President may, subject to the provisions of any law made by Parliament, by rule specify.
(6) The President shall cause all such reports to be laid before each House of Parliament.
(7) The President shall cause any report relating to a State to be laid before the Legislature of the State.
(8) Where any such report, or any part thereof, relates to any matter with which any State Government is concerned, a copy of such report shall be forwarded to the State Government which shall cause it to be laid before the Legislature of the State along with a memorandum explaining the action taken or proposed to be taken on the recommendations relating to the State and the reasons for the non-acceptance, if any, of any of such recommendations.
(9) The Union and every State Government shall consult the Commission on all major policy matters affecting the socially and educationally backward classes:
Provided that nothing in this clause shall apply for the purposes of clause (3) of article 342A.""",

    "342A": """(1) The President may with respect to any State or Union territory, and where it is a State, after consultation with the Governor thereof, by public notification, specify the socially and educationally backward classes in the Central List which shall for the purposes of the Central Government be deemed to be socially and educationally backward classes in relation to that State or Union territory, as the case may be.
(2) Parliament may by law include in or exclude from the Central List of socially and educationally backward classes specified in a notification issued under clause (1) any socially and educationally backward class, but save as aforesaid a notification issued under the said clause shall not be varied by any subsequent notification.
Explanation.—For the purposes of clauses (1) and (2), the expression “Central List” means the list of socially and educationally backward classes prepared and maintained by and for the Central Government.
(3) Notwithstanding anything contained in clauses (1) and (2), every State or Union territory may, by law, prepare and maintain, for its own purposes, a list of socially and educationally backward classes, entries in which may be different from the Central List."""
}

def update_manual():
    print("Updating missing articles manually...")
    count = 0
    for article_id, content in missing_articles.items():
        result = collection.update_one(
            {"articles.id": article_id},
            {"$set": {"articles.$[elem].content": content}},
            array_filters=[{"elem.id": article_id}]
        )
        if result.modified_count > 0:
            print(f"✓ Updated Article {article_id}")
            count += 1
        else:
            print(f"✗ Failed to update Article {article_id} (Not found in DB?)")
            
    print(f"Manually updated {count} articles.")

if __name__ == "__main__":
    update_manual()
