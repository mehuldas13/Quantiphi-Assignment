"""Content for the sample earnings-call transcripts.

All five companies are FICTIONAL. The figures are invented for this demo so the
dataset can ship inside a public repository without licensing questions. The
structure (operator intro, prepared remarks, CFO financial review, analyst Q&A)
mirrors a real earnings call so the search behaves the same way it would on
real transcripts.
"""

TRANSCRIPTS = [
    # ------------------------------------------------------------------ A
    {
        "file": "zentrix_cloud_q4_fy2025.pdf",
        "company": "Zentrix Cloud",
        "title": "Zentrix Cloud Inc. - Q4 FY2025 Earnings Call Transcript",
        "date": "February 4, 2026",
        "sections": [
            ("Operator", [
                "Good afternoon and welcome to the Zentrix Cloud fourth quarter and full fiscal year 2025 earnings conference call. Joining us today are Priya Raman, Chief Executive Officer, and Daniel Okafor, Chief Financial Officer. Please note that today's call contains forward-looking statements that involve risks and uncertainties.",
            ]),
            ("Priya Raman - Chief Executive Officer", [
                "Thank you, and good afternoon everyone. Q4 was a record quarter for Zentrix Cloud. We closed the year with momentum across every product line, and our AI Data Platform crossed 1,200 enterprise customers, up from 640 a year ago.",
                "Annual recurring revenue reached 2.31 billion dollars, an increase of 27 percent year over year. We added 48 new customers paying more than one million dollars annually, bringing that cohort to 412 customers.",
                "Our net revenue retention rate was 121 percent, which tells us existing customers continue to expand their usage. Customer churn remained below 4 percent for the full year.",
                "During the quarter we launched Zentrix Copilot, an assistant that lets analysts query their warehouse in plain English. More than 300 customers adopted Copilot within the first eight weeks.",
                "We also opened two new data centre regions in Frankfurt and Mumbai, which brings our footprint to 14 regions and helps customers meet data residency requirements.",
            ]),
            ("Daniel Okafor - Chief Financial Officer", [
                "Thanks, Priya. Total revenue for the fourth quarter was 612 million dollars, up 26 percent year over year and ahead of our guidance range of 595 to 600 million dollars. Subscription revenue was 571 million dollars, or 93 percent of total revenue.",
                "For the full fiscal year 2025, total revenue was 2.18 billion dollars, an increase of 25 percent compared with 1.74 billion dollars in fiscal 2024.",
                "Non-GAAP gross margin was 78.4 percent in Q4, up from 76.9 percent in the prior-year quarter, driven by better infrastructure utilisation.",
                "Non-GAAP operating income was 128 million dollars, representing an operating margin of 20.9 percent, compared with 15.2 percent a year ago. GAAP net income was 41 million dollars, or 0.29 dollars per diluted share.",
                "Free cash flow for the quarter was 164 million dollars, a free cash flow margin of 27 percent. We ended the year with 3.4 billion dollars in cash and marketable securities and no outstanding debt.",
                "Remaining performance obligations, or RPO, grew 31 percent to 3.9 billion dollars.",
                "Turning to guidance. For Q1 fiscal 2026 we expect revenue between 628 and 634 million dollars. For the full fiscal year 2026 we expect revenue between 2.70 and 2.73 billion dollars, representing growth of roughly 24 percent, and a non-GAAP operating margin of approximately 22 percent.",
            ]),
            ("Question and Answer Session", [
                "Analyst, Mark Liu, Harbor Securities: Congratulations on the quarter. Can you talk about what drove the gross margin expansion and whether it is sustainable?",
                "Daniel Okafor: Sure, Mark. Roughly two thirds of the improvement came from migrating workloads onto our own custom compute instances, and the rest from renegotiated cloud contracts. We believe gross margin in the 78 to 79 percent range is sustainable through fiscal 2026.",
                "Analyst, Sofia Marin, Crestline Partners: How should we think about Copilot monetisation?",
                "Priya Raman: Copilot is priced as an add-on at 20 percent of the base subscription. We are not including meaningful Copilot revenue in our fiscal 2026 guidance, so any faster adoption would be upside.",
                "Analyst, Mark Liu: What are the biggest risks you see for next year?",
                "Priya Raman: The main risks are longer enterprise sales cycles if the macro environment softens, and increasing competition from hyperscalers bundling analytics tools. We are investing heavily in differentiation through Copilot and our governance features.",
                "Operator: That concludes today's question and answer session. Thank you for participating.",
            ]),
        ],
    },
    # ------------------------------------------------------------------ B (Q4)
    {
        "file": "voltara_motors_q4_fy2025.pdf",
        "company": "Voltara Motors",
        "title": "Voltara Motors Corp. - Q4 FY2025 Earnings Call Transcript",
        "date": "January 28, 2026",
        "sections": [
            ("Operator", [
                "Welcome to the Voltara Motors fourth quarter 2025 earnings call. On the call today are Elena Brooks, Chief Executive Officer, and Rahul Mehta, Chief Financial Officer.",
            ]),
            ("Elena Brooks - Chief Executive Officer", [
                "Thank you. In the fourth quarter Voltara delivered 86,400 vehicles, a 34 percent increase over Q4 of last year and a quarterly record. Full-year deliveries were 301,000 vehicles, in line with the target of 300,000 we set at the start of the year.",
                "The new Voltara Aria compact SUV was the biggest contributor, accounting for 41 percent of fourth-quarter deliveries in its first full quarter of production.",
                "Our battery plant in Nevada reached a production rate of 22 gigawatt hours annualised, and our cost per kilowatt hour at the cell level fell 14 percent year over year.",
                "Our fast-charging network grew to 5,800 stalls across North America and Europe.",
            ]),
            ("Rahul Mehta - Chief Financial Officer", [
                "Thanks, Elena. Fourth quarter revenue was 4.12 billion dollars, an increase of 29 percent year over year. Automotive revenue was 3.67 billion dollars, and energy and services revenue was 450 million dollars.",
                "Full-year 2025 revenue was 14.6 billion dollars, compared with 11.2 billion dollars in 2024, an increase of 30 percent.",
                "Automotive gross margin was 17.8 percent in Q4, compared with 15.1 percent in Q3 and 13.9 percent in the fourth quarter of last year. The improvement reflects lower battery costs and better fixed-cost absorption at higher volume.",
                "Operating income was 238 million dollars, our third consecutive profitable quarter, for an operating margin of 5.8 percent. Net income was 176 million dollars, or 0.52 dollars per diluted share.",
                "Free cash flow was 312 million dollars in the quarter. Capital expenditure was 690 million dollars, mostly for the second phase of the Nevada battery plant. We ended the year with 6.1 billion dollars in cash.",
                "For 2026 we are guiding to deliveries of 380,000 to 400,000 vehicles and automotive gross margin of 18 to 20 percent. We expect capital expenditure of 2.8 to 3.0 billion dollars.",
            ]),
            ("Question and Answer Session", [
                "Analyst, James Porter, Redwood Capital: What drove the sequential improvement in automotive margin from Q3?",
                "Rahul Mehta: About half came from battery cost reductions, a quarter from Aria reaching scale, and the rest from lower logistics costs. Pricing was roughly flat quarter over quarter.",
                "Analyst, Hannah Cole, Northgate Research: Are you seeing any demand softness given the change in EV tax credits?",
                "Elena Brooks: Order backlog entering Q1 is 61,000 vehicles, up from 48,000 entering Q4. We are seeing some softness in the United States premium segment, but Europe and the Aria demand more than offset it.",
                "Analyst, James Porter: Can you give an update on the autonomous driving programme?",
                "Elena Brooks: Our Level 3 highway system, Voltara Pilot, received regulatory approval in Germany in December and we plan a United States launch in the second half of 2026.",
            ]),
        ],
    },
    # ------------------------------------------------------------------ B (Q3)
    {
        "file": "voltara_motors_q3_fy2025.pdf",
        "company": "Voltara Motors",
        "title": "Voltara Motors Corp. - Q3 FY2025 Earnings Call Transcript",
        "date": "October 22, 2025",
        "sections": [
            ("Operator", [
                "Welcome to the Voltara Motors third quarter 2025 earnings call with Elena Brooks, Chief Executive Officer, and Rahul Mehta, Chief Financial Officer.",
            ]),
            ("Elena Brooks - Chief Executive Officer", [
                "In the third quarter we delivered 77,900 vehicles, up 28 percent year over year. Production of the Aria compact SUV started in August and ramped faster than planned.",
                "We remain on track to deliver approximately 300,000 vehicles for the full year.",
            ]),
            ("Rahul Mehta - Chief Financial Officer", [
                "Third quarter revenue was 3.74 billion dollars, up 27 percent year over year. Automotive gross margin was 15.1 percent, compared with 14.2 percent in Q2.",
                "Operating income was 121 million dollars, an operating margin of 3.2 percent. Net income was 88 million dollars, or 0.26 dollars per diluted share.",
                "Free cash flow was 95 million dollars and we ended the quarter with 5.7 billion dollars in cash.",
                "Aria launch costs reduced automotive gross margin by roughly 120 basis points in the quarter; we expect those costs to fade in Q4.",
            ]),
            ("Question and Answer Session", [
                "Analyst, Hannah Cole, Northgate Research: When do you expect the Aria to reach full production rate?",
                "Elena Brooks: We expect to reach the full rate of 2,500 units per week by the end of the fourth quarter.",
            ]),
        ],
    },
    # ------------------------------------------------------------------ C
    {
        "file": "medivane_therapeutics_q4_fy2025.pdf",
        "company": "Medivane Therapeutics",
        "title": "Medivane Therapeutics plc - Q4 FY2025 Earnings Call Transcript",
        "date": "February 11, 2026",
        "sections": [
            ("Operator", [
                "Good morning and welcome to Medivane Therapeutics' fourth quarter and full year 2025 results call. Presenting today are Dr. Thomas Weller, Chief Executive Officer, and Grace Adeyemi, Chief Financial Officer.",
            ]),
            ("Dr. Thomas Weller - Chief Executive Officer", [
                "Thank you. 2025 was a transformational year for Medivane. Our lead product Cardiolex, for chronic heart failure, generated 1.05 billion dollars in sales in its second full year on the market and became our first blockbuster.",
                "In November our Phase 3 trial of Neurovane in early Alzheimer's disease met its primary endpoint, showing a 31 percent slowing of cognitive decline versus placebo. We plan to file with the FDA in the second quarter of 2026.",
                "Our pipeline now includes 14 clinical programmes, five of which are in Phase 3.",
            ]),
            ("Grace Adeyemi - Chief Financial Officer", [
                "Thank you, Thomas. Total revenue for the fourth quarter was 842 million dollars, up 38 percent year over year. Product sales were 794 million dollars and collaboration revenue was 48 million dollars.",
                "Cardiolex sales were 301 million dollars in Q4, up 52 percent year over year. Our oncology franchise contributed 352 million dollars.",
                "Full-year revenue was 3.02 billion dollars, an increase of 33 percent from 2.27 billion dollars in 2024.",
                "Research and development expense was 298 million dollars in the quarter, or 35 percent of revenue, reflecting the Neurovane Phase 3 programme.",
                "Gross margin was 84.5 percent. Operating income was 156 million dollars and diluted earnings per share were 0.74 dollars.",
                "We ended the year with 2.6 billion dollars in cash. For 2026 we expect total revenue of 3.6 to 3.8 billion dollars and R&D expense of approximately 1.3 billion dollars.",
            ]),
            ("Question and Answer Session", [
                "Analyst, Olivia Grant, Meridian Bank: How should we think about the launch timeline for Neurovane?",
                "Dr. Thomas Weller: Assuming a standard review, we would expect approval in the first half of 2027. We are already building a specialist sales force of around 400 representatives.",
                "Analyst, Victor Shah, Lakeside Equity: Are there any patent risks for Cardiolex?",
                "Grace Adeyemi: Cardiolex is protected by composition-of-matter patents until 2036 in the United States and 2037 in Europe.",
            ]),
        ],
    },
    # ------------------------------------------------------------------ D
    {
        "file": "solvane_energy_q4_fy2025.pdf",
        "company": "Solvane Energy",
        "title": "Solvane Energy Holdings - Q4 FY2025 Earnings Call Transcript",
        "date": "February 18, 2026",
        "sections": [
            ("Operator", [
                "Welcome to the Solvane Energy fourth quarter 2025 earnings call. Speaking today are Marcus Lindqvist, Chief Executive Officer, and Aisha Karim, Chief Financial Officer.",
            ]),
            ("Marcus Lindqvist - Chief Executive Officer", [
                "Thank you. Solvane added 2.4 gigawatts of new solar and wind capacity in 2025, bringing our operating portfolio to 11.8 gigawatts across nine countries.",
                "Our battery storage business commissioned 1.1 gigawatt hours of storage during the year, and storage now represents 18 percent of our development pipeline.",
                "We signed long-term power purchase agreements with three large technology companies for data centre supply, totalling 1.6 gigawatts.",
            ]),
            ("Aisha Karim - Chief Financial Officer", [
                "Thanks, Marcus. Fourth quarter revenue was 1.38 billion dollars, up 19 percent year over year, driven by new capacity coming online and higher contracted power prices.",
                "Full-year revenue was 5.21 billion dollars compared with 4.47 billion dollars in 2024, an increase of 17 percent.",
                "Adjusted EBITDA for Q4 was 742 million dollars, an adjusted EBITDA margin of 54 percent. Net income was 205 million dollars, or 0.61 dollars per share.",
                "Our net debt to EBITDA ratio improved to 4.1 times from 4.6 times a year ago. We raised our quarterly dividend by 8 percent to 0.27 dollars per share.",
                "For 2026 we expect adjusted EBITDA of 3.1 to 3.3 billion dollars and plan to add 2.8 to 3.2 gigawatts of new capacity.",
            ]),
            ("Question and Answer Session", [
                "Analyst, Ben Okoro, Summit Advisors: How exposed are you to interest rate changes?",
                "Aisha Karim: About 88 percent of our debt is fixed rate with an average maturity of 9 years, so near-term rate moves have a limited effect on earnings.",
                "Analyst, Clara Novak, Alpine Research: What is driving the demand from technology companies?",
                "Marcus Lindqvist: AI data centres need firm, clean power around the clock. Pairing our solar with battery storage lets us offer 24-hour contracts at a premium price.",
            ]),
        ],
    },
    # ------------------------------------------------------------------ E
    {
        "file": "brightmart_retail_q4_fy2025.pdf",
        "company": "Brightmart Retail",
        "title": "Brightmart Retail Group - Q4 FY2025 Earnings Call Transcript",
        "date": "March 3, 2026",
        "sections": [
            ("Operator", [
                "Good morning and welcome to the Brightmart Retail Group fourth quarter fiscal 2025 earnings call. With us today are Sarah Whitfield, Chief Executive Officer, and Kenji Tanaka, Chief Financial Officer.",
            ]),
            ("Sarah Whitfield - Chief Executive Officer", [
                "Thank you. The holiday quarter was strong for Brightmart. Comparable store sales grew 5.8 percent, with traffic up 3.1 percent and average ticket up 2.6 percent.",
                "Digital sales grew 22 percent and now represent 24 percent of total sales. Same-day delivery is available from 1,150 of our 1,420 stores.",
                "Our Brightmart Plus membership programme reached 9.3 million paying members, up 1.7 million over the year.",
            ]),
            ("Kenji Tanaka - Chief Financial Officer", [
                "Thanks, Sarah. Fourth quarter net sales were 18.9 billion dollars, an increase of 7.2 percent year over year.",
                "Full-year net sales were 64.3 billion dollars, up 6.1 percent from 60.6 billion dollars in fiscal 2024.",
                "Gross margin was 27.6 percent in Q4, down 40 basis points year over year due to holiday promotions and a higher mix of grocery sales.",
                "Operating income was 1.04 billion dollars, an operating margin of 5.5 percent. Diluted earnings per share were 2.31 dollars compared with 2.05 dollars last year.",
                "Inventory at year end was 9.8 billion dollars, down 3 percent year over year despite higher sales, reflecting better inventory management.",
                "For fiscal 2026 we expect comparable sales growth of 3 to 4 percent and diluted earnings per share of 7.40 to 7.70 dollars. We plan to open 45 new stores.",
            ]),
            ("Question and Answer Session", [
                "Analyst, Ravi Desai, Pinecrest Capital: How is the membership programme affecting profitability?",
                "Kenji Tanaka: Members shop 2.4 times more often than non-members, and membership fee income contributed roughly 30 basis points to operating margin this year.",
                "Analyst, Laura Kim, Oakmont Securities: What is your outlook for tariffs and consumer spending?",
                "Sarah Whitfield: We have diversified sourcing so that no single country accounts for more than 25 percent of imported goods. Consumers remain value focused, which plays to our strengths.",
            ]),
        ],
    },
]
