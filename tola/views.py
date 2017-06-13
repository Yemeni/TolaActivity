from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from tola.forms import RegistrationForm, NewUserRegistrationForm, NewTolaUserRegistrationForm, BookmarkForm
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from workflow.models import WorkflowLevel2, WorkflowLevel1, SiteProfile, Sector,Country, TolaUser,TolaSites, TolaBookmarks, FormGuidance
from indicators.models import CollectedData, Indicator

from tola.tables import IndicatorDataTable
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q, Count
from tola.util import getCountry
from django.contrib.auth.models import Group

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@login_required(login_url='/accounts/login/')
def index(request, selected_countries=None, id=0, sector=0):
    """
    Home page
    get count of agreements approved and total for dashboard
    """
    workflowlevel1_id = id
    user_countries = getCountry(request.user)

    if not selected_countries:
        selected_countries = user_countries
        selected_countries_list = None
        selected_countries_label_list = None
    else:
        #transform to list if a submitted country
        selected_countries = [selected_countries]
        selected_countries_list = Country.objects.all().filter(id__in=selected_countries)
        selected_countries_label_list = Country.objects.all().filter(id__in=selected_countries).values('country')

    getAgencySite = TolaSites.objects.all().filter(id=1)
    getSectors = Sector.objects.all().exclude(workflowlevel1__isnull=True).select_related()

    #limit the workflowlevel1s by the selected sector
    if int(sector) == 0:
        getworkflowlevel1s = WorkflowLevel1.objects.all().prefetch_related('agreement', 'agreement__office').filter(funding_status="Funded", country__in=selected_countries).exclude(agreement__isnull=True)
        sectors = Sector.objects.all()
    else:
        getworkflowlevel1s = WorkflowLevel1.objects.all().filter(funding_status="Funded", country__in=selected_countries, sector=sector).exclude(agreement__isnull=True)
        sectors = Sector.objects.all().filter(id=sector)

    #get data for just one workflowlevel1 or all workflowlevel1s
    if int(workflowlevel1_id) == 0:
        getFilteredName=None
        #filter by all workflowlevel1s then filter by sector if found
        if int(sector) > 0:
            getSiteProfile = SiteProfile.objects.all().prefetch_related('country','district','province').filter(Q(Q(projectagreement__sector__in=sectors)), country__in=selected_countries).filter(status=1)
            getSiteProfileIndicator = SiteProfile.objects.all().prefetch_related('country','district','province').filter(Q(collecteddata__workflowlevel1__country__in=selected_countries)).filter(status=1)
            agreement_total_count = WorkflowLevel2.objects.all().filter(sector__in=sectors,workflowlevel1__country__in=selected_countries).count()
            complete_total_count = WorkflowLevel2.objects.all().filter(project_agreement__sector__in=sectors,workflowlevel1__country__in=selected_countries).count()
            agreement_approved_count = WorkflowLevel2.objects.all().filter(approval='approved', sector__in=sectors,workflowlevel1__country__in=selected_countries).count()
            complete_approved_count = WorkflowLevel2.objects.all().filter(approval='approved', project_agreement__sector__in=sectors,workflowlevel1__country__in=selected_countries).count()

            agreement_awaiting_count = WorkflowLevel2.objects.all().filter(approval='awaiting approval', sector__in=sectors,workflowlevel1__country__in=selected_countries).count()

            complete_awaiting_count = WorkflowLevel2.objects.all().filter(approval='awaiting approval', project_agreement__sector__in=sectors,workflowlevel1__country__in=selected_countries).count()

            agreement_open_count = WorkflowLevel2.objects.all().filter(Q(Q(approval='open') | Q(approval="") | Q(approval=None)), sector__id__in=sectors,workflowlevel1__country__in=selected_countries).count()
            complete_open_count = WorkflowLevel2.objects.all().filter(Q(Q(approval='open') | Q(approval="") | Q(approval=None)), project_agreement__sector__in=sectors,workflowlevel1__country__in=selected_countries).count()
            agreement_wait_count = WorkflowLevel2.objects.all().filter(Q(approval='in progress') & Q(Q(approval='in progress') | Q(approval=None) | Q(approval="")), sector__in=sectors,workflowlevel1__country__in=selected_countries).count()
            complete_wait_count = WorkflowLevel2.objects.all().filter(Q(approval='in progress') & Q(Q(approval='in progress') | Q(approval=None) | Q(approval="")), project_agreement__sector__in=sectors,workflowlevel1__country__in=selected_countries).count()
            getQuantitativeDataSums = CollectedData.objects.all().filter(Q(agreement__sector__in=sectors), indicator__key_performance_indicator=True, targeted__isnull=False, indicator__workflowlevel1__country__in=selected_countries).exclude(targeted=None,workflowlevel1__funding_status="Archived").order_by('indicator__workflowlevel1','indicator__number').values('indicator__workflowlevel1__name','indicator__number','indicator__name','indicator__id').annotate(targets=Sum('targeted'), actuals=Sum('achieved'))
        else:
            getSiteProfile = SiteProfile.objects.all().prefetch_related('country','district','province').filter(country__in=selected_countries).filter(status=1)
            getSiteProfileIndicator = SiteProfile.objects.all().prefetch_related('country','district','province').filter(Q(collecteddata__workflowlevel1__country__in=selected_countries)).filter(status=1)
            agreement_total_count = WorkflowLevel2.objects.all().filter(workflowlevel1__country__in=selected_countries).count()
            complete_total_count = WorkflowLevel2.objects.all().filter(workflowlevel1__country__in=selected_countries).count()
            agreement_approved_count = WorkflowLevel2.objects.all().filter(approval='approved',workflowlevel1__country__in=selected_countries).count()
            complete_approved_count = WorkflowLevel2.objects.all().filter(approval='approved',workflowlevel1__country__in=selected_countries).count()

            agreement_awaiting_count = WorkflowLevel2.objects.all().filter(approval='awaiting approval',workflowlevel1__country__in=selected_countries).count()
            complete_awaiting_count = WorkflowLevel2.objects.all().filter(approval='awaiting approval',workflowlevel1__country__in=selected_countries).count()

            agreement_open_count = WorkflowLevel2.objects.all().filter(Q(Q(approval='open') | Q(approval="") | Q(approval=None)),workflowlevel1__country__in=selected_countries).count()
            complete_open_count = WorkflowLevel2.objects.all().filter(Q(Q(approval='open') | Q(approval="") | Q(approval=None)),workflowlevel1__country__in=selected_countries).count()
            agreement_wait_count = WorkflowLevel2.objects.all().filter(Q(approval='in progress') & Q(Q(approval='in progress') | Q(approval=None) | Q(approval="")),workflowlevel1__country__in=selected_countries).count()
            complete_wait_count = WorkflowLevel2.objects.all().filter(Q(approval='in progress') & Q(Q(approval='in progress') | Q(approval=None) | Q(approval="")),workflowlevel1__country__in=selected_countries).count()
            getQuantitativeDataSums = CollectedData.objects.all().filter(indicator__key_performance_indicator=True, achieved__isnull=False, targeted__isnull=False, indicator__workflowlevel1__country__in=selected_countries).exclude(achieved=None,targeted=None,workflowlevel1__funding_status="Archived").order_by('indicator__workflowlevel1','indicator__number').values('indicator__workflowlevel1__name','indicator__number','indicator__name','indicator__id').annotate(targets=Sum('targeted'), actuals=Sum('achieved'))
    else:
        getFilteredName=WorkflowLevel1.objects.get(id=workflowlevel1_id)
        agreement_total_count = WorkflowLevel2.objects.all().filter(workflowlevel1__id=workflowlevel1_id).count()
        complete_total_count = WorkflowLevel2.objects.all().filter(workflowlevel1__id=workflowlevel1_id).count()
        agreement_approved_count = WorkflowLevel2.objects.all().filter(workflowlevel1__id=workflowlevel1_id, approval='approved').count()
        complete_approved_count = WorkflowLevel2.objects.all().filter(workflowlevel1__id=workflowlevel1_id, approval='approved').count()
        agreement_open_count = WorkflowLevel2.objects.all().filter(workflowlevel1__id=workflowlevel1_id, approval='open').count()
        complete_open_count = WorkflowLevel2.objects.all().filter(Q(Q(approval='open') | Q(approval="")),workflowlevel1__id=workflowlevel1_id).count()
        agreement_wait_count = WorkflowLevel2.objects.all().filter(Q(workflowlevel1__id=workflowlevel1_id), Q(approval='in progress') & Q(Q(approval='in progress') | Q(approval=None) | Q(approval=""))).count()
        complete_wait_count = WorkflowLevel2.objects.all().filter(Q(workflowlevel1__id=workflowlevel1_id), Q(approval='in progress') & Q(Q(approval='in progress') | Q(approval=None) | Q(approval=""))).count()
        getSiteProfile = SiteProfile.objects.all().prefetch_related('country','district','province').filter(projectagreement__workflowlevel1__id=workflowlevel1_id).filter(status=1)
        getSiteProfileIndicator = SiteProfile.objects.all().prefetch_related('country','district','province').filter(Q(collecteddata__workflowlevel1__id=workflowlevel1_id)).filter(status=1)
        getQuantitativeDataSums = CollectedData.objects.all().filter(indicator__key_performance_indicator=True, indicator__workflowlevel1__id=workflowlevel1_id,achieved__isnull=False).exclude(achieved=None,targeted=None,workflowlevel1__funding_status="Archived").order_by('indicator__level1','indicator__number').values('indicator__workflowlevel1__name','indicator__number','indicator__name','indicator__id').annotate(targets=Sum('targeted'), actuals=Sum('achieved'))

        agreement_awaiting_count = WorkflowLevel2.objects.all().filter(workflowlevel1__id=workflowlevel1_id, approval='awaiting approval').count()
        complete_awaiting_count = WorkflowLevel2.objects.all().filter(workflowlevel1__id=workflowlevel1_id, approval='awaiting approval').count()

    #Evidence and Objectives are for the global leader dashboard items and are the same every time
    count_evidence = CollectedData.objects.all().filter(indicator__isnull=False).values("indicator__workflowlevel1__country__country").annotate(evidence_count=Count('evidence', distinct=True) + Count('tola_table', distinct=True),indicator_count=Count('pk', distinct=True)).order_by('-evidence_count')
    getObjectives = CollectedData.objects.all().filter(indicator__strategic_objectives__isnull=False, indicator__workflowlevel1__country__in=selected_countries).exclude(achieved=None,targeted=None).order_by('indicator__strategic_objectives__name').values('indicator__strategic_objectives__name').annotate(indicators=Count('pk', distinct=True),targets=Sum('targeted'), actuals=Sum('achieved'))
    table = IndicatorDataTable(getQuantitativeDataSums)
    table.paginate(page=request.GET.get('page', 1), per_page=20)

    count_workflowlevel1 = WorkflowLevel1.objects.all().filter(country__in=selected_countries, funding_status='Funded').count()

    approved_by = TolaUser.objects.get(user_id=request.user)
    user_pending_approvals = WorkflowLevel2.objects.all().filter(approved_by=approved_by).exclude(approval='approved').count()

    count_workflowlevel1_agreement = WorkflowLevel2.objects.all().filter(workflowlevel1__country__in=selected_countries,workflowlevel1__funding_status='Funded').values('workflowlevel1').distinct().count()
    count_indicator = Indicator.objects.all().filter(workflowlevel1__country__in=selected_countries,workflowlevel1__funding_status='Funded').values('workflowlevel1').distinct().count()
    count_evidence_adoption = CollectedData.objects.all().filter(indicator__isnull=False,indicator__workflowlevel1__country__in=selected_countries).values("indicator__workflowlevel1__country__country").annotate(evidence_count=Count('evidence', distinct=True) + Count('tola_table', distinct=True),indicator_count=Count('pk', distinct=True)).order_by('-evidence_count')
    count_workflowlevel1 = int(count_workflowlevel1)
    count_workflowlevel1_agreement = int(count_workflowlevel1_agreement)

    green = "#5CB85C"
    yellow = "#E89424"
    red = "#B30838"

    # 66% or higher = Green above 25% below %66 is Orange and below %25 is Red

    if count_workflowlevel1_agreement >= float(count_workflowlevel1/1.5):
        workflow_adoption = green
    elif count_workflowlevel1_agreement < count_workflowlevel1/1.5 and count_workflowlevel1_agreement > count_workflowlevel1/4:
        workflow_adoption = yellow
    elif count_workflowlevel1_agreement <= count_workflowlevel1/4:
        workflow_adoption = red

    if count_indicator >= float(count_workflowlevel1/1.5):
        indicator_adoption = green
    elif count_indicator < count_workflowlevel1/1.5 and count_indicator > count_workflowlevel1/4:
        indicator_adoption = yellow
    elif count_indicator <= count_workflowlevel1/4:
        indicator_adoption = red

    total_evidence_adoption_count = 0
    total_indicator_data_count = 0
    for country in count_evidence_adoption:
        total_evidence_adoption_count = total_evidence_adoption_count + country['evidence_count']
        total_indicator_data_count = total_indicator_data_count + country['indicator_count']

    if total_evidence_adoption_count >= float(total_indicator_data_count/1.5):
        evidence_adoption = green
    elif total_evidence_adoption_count < total_indicator_data_count/1.5 and total_evidence_adoption_count > total_indicator_data_count/4:
        evidence_adoption = yellow
    elif total_evidence_adoption_count <= total_indicator_data_count/4:
        evidence_adoption = red

    return render(request, "index.html", {'agreement_total_count':agreement_total_count,
                                          'agreement_approved_count':agreement_approved_count,
                                          'agreement_open_count':agreement_open_count,
                                          'agreement_wait_count':agreement_wait_count,
                                          'agreement_awaiting_count':agreement_awaiting_count,
                                          'complete_open_count':complete_open_count,
                                          'complete_approved_count':complete_approved_count,'complete_total_count':complete_total_count,
                                          'complete_wait_count':complete_wait_count,
                                          'complete_awaiting_count':complete_awaiting_count,
                                          'workflowlevel1s':getworkflowlevel1s,'getSiteProfile':getSiteProfile,
                                          'countries': user_countries,'selected_countries':selected_countries,
                                          'getFilteredName':getFilteredName,'getSectors':getSectors,
                                          'sector': sector, 'table': table, 'getQuantitativeDataSums':getQuantitativeDataSums,
                                          'count_evidence':count_evidence,
                                          'getObjectives':getObjectives,
                                          'selected_countries_list': selected_countries_list,
                                          'getSiteProfileIndicator': getSiteProfileIndicator,
                                          'getAgencySite': getAgencySite,
                                          'workflow_adoption': workflow_adoption,
                                          'count_workflowlevel1': count_workflowlevel1,
                                          'count_workflowlevel1_agreement': count_workflowlevel1_agreement,
                                          'indicator_adoption': indicator_adoption,
                                          'count_indicator': count_indicator,
                                          'evidence_adoption': evidence_adoption,
                                          'count_evidence_adoption':total_evidence_adoption_count,
                                          'count_indicator_data':total_indicator_data_count,
                                          'selected_countries_label_list':selected_countries_label_list,
                                          'user_pending_approvals':user_pending_approvals,
                                          })


def register(request):
    """
    Register a new User profile using built in Django Users Model
    """
    privacy = TolaSites.objects.get(id=1)
    if request.method == 'POST':
        uf = NewUserRegistrationForm(request.POST)
        tf = NewTolaUserRegistrationForm(request.POST)

        if uf.is_valid() * tf.is_valid():
            user = uf.save()
            user.groups.add(Group.objects.get(name='ViewOnly'))

            tolauser = tf.save(commit=False)
            tolauser.user = user
            tolauser.save()
            messages.error(request, 'Thank you, You have been registered as a new user.', fail_silently=False)
            return HttpResponseRedirect("/")
    else:
        uf = NewUserRegistrationForm()
        tf = NewTolaUserRegistrationForm()

    return render(request, "registration/register.html", {
        'userform': uf,'tolaform': tf, 'helper': NewTolaUserRegistrationForm.helper,'privacy':privacy
    })


def profile(request):
    """
    Update a User profile using built in Django Users Model if the user is logged in
    otherwise redirect them to registration version
    """
    if request.user.is_authenticated():
        obj = get_object_or_404(TolaUser, user=request.user)
        form = RegistrationForm(request.POST or None, instance=obj,initial={'username': request.user})

        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.error(request, 'Your profile has been updated.', fail_silently=False)

        return render(request, "registration/profile.html", {
            'form': form, 'helper': RegistrationForm.helper
        })
    else:
        return HttpResponseRedirect("/accounts/register")


class BookmarkList(ListView):
    """
    Bookmark Report filtered by project
    """
    model = TolaBookmarks
    template_name = 'registration/bookmark_list.html'

    def get(self, request, *args, **kwargs):
        getUser = TolaUser.objects.all().filter(user=request.user)
        getBookmarks = TolaBookmarks.objects.all().filter(user=getUser)

        return render(request, self.template_name, {'getBookmarks':getBookmarks})


class BookmarkCreate(CreateView):
    """
    Using Bookmark Form for new bookmark per user
    """
    model = TolaBookmarks
    template_name = 'registration/bookmark_form.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Bookmarks")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(BookmarkCreate, self).dispatch(request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(BookmarkCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):

        initial = {
            'user': self.request.user,
        }

        return initial

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Bookmark Created!')
        latest = TolaBookmarks.objects.latest('id')
        redirect_url = '/bookmark_update/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = BookmarkForm


class BookmarkUpdate(UpdateView):
    """
    Bookmark Form Update an existing site profile
    """
    model = TolaBookmarks
    template_name = 'registration/bookmark_form.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Bookmarks")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(BookmarkUpdate, self).dispatch(request, *args, **kwargs)

    def get_initial(self):

        initial = {
            'user': self.request.user,
        }

        return initial

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Bookmark Updated!')
        latest = TolaBookmarks.objects.latest('id')
        redirect_url = '/bookmark_update/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = BookmarkForm


class BookmarkDelete(DeleteView):
    """
    Bookmark Form Delete an existing bookmark
    """
    model = TolaBookmarks
    template_name = 'registration/bookmark_confirm_delete.html'
    success_url = "/bookmark_list"

    def dispatch(self, request, *args, **kwargs):
        return super(BookmarkDelete, self).dispatch(request, *args, **kwargs)

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()

        messages.success(self.request, 'Success, Bookmark Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = BookmarkForm


def logout_view(request):
    """
    Logout a user
    """
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/")

