"""
Views for user API
"""

from courseware.access import is_mobile_available_for_user
from openedx.features.course_duration_limits.access import check_course_expired

from mobile_api.decorators import mobile_view
from mobile_api.v1.users.serializers import CourseEnrollmentSerializer
from mobile_api.users.views import UserCourseEnrollmentsList as UserCourseEnrollmentsListBase


@mobile_view(is_user=True)
class UserCourseEnrollmentsList(UserCourseEnrollmentsListBase):
    """
    **Use Case**

        Get information about the courses that the currently signed in user is
        enrolled in.

        This differs from v0.5 version by returning ALL enrollments for
        a user rather than only the enrollments the user has access to (that haven't expired).
        An additional attribute "expiration" has been added to the response, which lists the date
        when access to the course will expire or null if it doesn't expire.

    **Example Request**

        GET /api/mobile/v1/users/{username}/course_enrollments/

    **Response Values**

        If the request for information about the user is successful, the
        request returns an HTTP 200 "OK" response.

        The HTTP 200 response has the following values.

        * expiration: The course expiration date for given user course pair
          or null if the course does not expire.
        * certificate: Information about the user's earned certificate in the
          course.
        * course: A collection of the following data about the course.

        * courseware_access: A JSON representation with access information for the course,
          including any access errors.

          * course_about: The URL to the course about page.
          * course_sharing_utm_parameters: Encoded UTM parameters to be included in course sharing url
          * course_handouts: The URI to get data for course handouts.
          * course_image: The path to the course image.
          * course_updates: The URI to get data for course updates.
          * discussion_url: The URI to access data for course discussions if
            it is enabled, otherwise null.
          * end: The end date of the course.
          * id: The unique ID of the course.
          * name: The name of the course.
          * number: The course number.
          * org: The organization that created the course.
          * start: The date and time when the course starts.
          * start_display:
            If start_type is a string, then the advertised_start date for the course.
            If start_type is a timestamp, then a formatted date for the start of the course.
            If start_type is empty, then the value is None and it indicates that the course has not yet started.
          * start_type: One of either "string", "timestamp", or "empty"
          * subscription_id: A unique "clean" (alphanumeric with '_') ID of
            the course.
          * video_outline: The URI to get the list of all videos that the user
            can access in the course.

        * created: The date the course was created.
        * is_active: Whether the course is currently active. Possible values
          are true or false.
        * mode: The type of certificate registration for this course (honor or
          certified).
        * url: URL to the downloadable version of the certificate, if exists.
    """
    serializer_class = CourseEnrollmentSerializer

    def get_queryset(self):
        enrollments = self.queryset.filter(
            user__username=self.kwargs['username'],
            is_active=True
        ).order_by('created').reverse()
        org = self.request.query_params.get('org', None)
        return [
            enrollment for enrollment in enrollments
            if enrollment.course_overview and self.is_org(org, enrollment.course_overview.org) and
            is_mobile_available_for_user(self.request.user, enrollment.course_overview)
        ]
