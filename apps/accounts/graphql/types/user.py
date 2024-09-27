from ariadne import gql

accounts = gql("""
    type User {
        id: ID!
        phone: Int
        user_type: String
        user_subtype: String
        email: String
        enterprise_name: String
        profile_id: Profile!
    }
""")