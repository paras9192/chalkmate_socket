from apps.classes.graphql import class_resolvers
from apps.userProfile.graphql import profile_resolvers
from apps.assignments.graphql import quiz_resolvers
from apps.groups.graphql import group_resolvers
from apps.lecturePlan.graphql import lec_resolvers
from apps.gradebook.graphql import gradebook_resolvers

resolvers = [
    *class_resolvers,
    *profile_resolvers,
    *quiz_resolvers,
    *group_resolvers,
    *lec_resolvers,
    *gradebook_resolvers
]