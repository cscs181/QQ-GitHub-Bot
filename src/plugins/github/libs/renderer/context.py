"""
@Author         : yanyongyu
@Date           : 2023-10-18 16:20:28
@LastEditors    : yanyongyu
@LastEditTime   : 2024-08-18 17:29:14
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Self, Literal, TypeAlias, TypedDict

from nonebot import logger
from unidiff import PatchSet
from githubkit.versions.latest import models
from nonebot.adapters.github import OAuthBot, GitHubBot

from .utils import (
    get_repo_from_issue,
    get_comment_reactions,
    get_issue_label_color,
    get_diff_from_pull_request,
    get_pull_request_from_issue,
)


@dataclass(frozen=True, kw_only=True)
class RepoInfo:
    owner: str
    name: str

    private: bool
    fork: bool
    is_template: bool

    parent_full_name: str | None
    template_full_name: str | None

    forks_count: int
    stargazers_count: int

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"

    @classmethod
    def from_repo(cls, repo: models.FullRepository) -> Self:
        return cls(
            owner=repo.owner.login,
            name=repo.name,
            private=repo.private,
            fork=repo.fork,
            is_template=bool(repo.is_template),
            parent_full_name=repo.parent.full_name if repo.parent else None,
            template_full_name=(
                repo.template_repository.full_name if repo.template_repository else None
            ),
            forks_count=repo.forks_count,
            stargazers_count=repo.stargazers_count,
        )

    @classmethod
    def from_webhook(cls, repo: models.RepositoryWebhooks) -> Self:
        return cls(
            owner=repo.owner.login,
            name=repo.name,
            private=repo.private,
            fork=repo.fork,
            is_template=bool(repo.is_template),
            parent_full_name=None,
            template_full_name=(
                repo.template_repository.full_name
                if repo.template_repository and repo.template_repository.full_name
                else None
            ),
            forks_count=repo.forks_count,
            stargazers_count=repo.stargazers_count,
        )


@dataclass(frozen=True, kw_only=True)
class IssueInfo:
    number: int
    title: str

    state: str
    state_reason: str | None
    draft: bool

    user: str
    user_avatar: str
    author_association: str
    created_at: datetime
    comments: int

    body_html: str | None
    body: str | None
    reactions: dict[str, int]

    @classmethod
    def from_issue(cls, issue: models.Issue) -> Self:
        return cls(
            number=issue.number,
            title=issue.title,
            state=issue.state,
            state_reason=issue.state_reason if issue.state_reason else None,
            draft=bool(issue.draft),
            user=issue.user.login if issue.user else "ghost",
            user_avatar=(
                issue.user.avatar_url if issue.user else "https://github.com/ghost.png"
            ),
            author_association=issue.author_association,
            created_at=issue.created_at,
            comments=issue.comments,
            body_html=issue.body_html if issue.body_html else None,
            body=issue.body if issue.body else None,
            reactions=(
                get_comment_reactions(issue.reactions) if issue.reactions else {}
            ),
        )

    @classmethod
    def from_webhook(
        cls,
        issue: (
            models.WebhookIssuesOpenedPropIssue
            | models.WebhookIssuesClosedPropIssue
            | models.WebhookIssueCommentCreatedPropIssue
            | models.WebhookIssueCommentEditedPropIssue
        ),
    ) -> Self:
        if issue.state:
            state = issue.state
        elif isinstance(issue, models.WebhookIssuesOpenedPropIssue):
            state = "open"
        elif isinstance(issue, models.WebhookIssuesClosedPropIssue):
            state = "closed"
        else:
            state = issue.state

        return cls(
            number=issue.number,
            title=issue.title,
            state=state,
            state_reason=issue.state_reason if issue.state_reason else None,
            draft=bool(issue.draft),
            user=issue.user.login if issue.user else "ghost",
            user_avatar=(
                issue.user.avatar_url
                if issue.user and issue.user.avatar_url
                else "https://github.com/ghost.png"
            ),
            author_association=issue.author_association,
            created_at=issue.created_at,
            comments=issue.comments,
            body_html=None,
            body=issue.body if issue.body else None,
            reactions=(
                get_comment_reactions(issue.reactions) if issue.reactions else {}
            ),
        )


@dataclass(frozen=True, kw_only=True)
class PullRequestInfo:
    number: int
    title: str

    state: str
    merged: bool
    draft: bool

    user: str
    user_avatar: str
    author_association: str
    merged_by: str | None
    commits: int

    base_owner: str
    base_label: str
    base_ref: str

    head_owner: str | None
    head_label: str
    head_ref: str

    merged_at: datetime | None
    created_at: datetime

    body_html: str | None
    body: str | None
    reactions: dict[str, int]

    @classmethod
    def from_pr(
        cls,
        issue: (
            models.Issue
            | models.WebhookIssueCommentCreatedPropIssue
            | models.WebhookIssueCommentEditedPropIssue
        ),
        pr: models.PullRequest,
    ) -> Self:
        return cls(
            number=pr.number,
            title=pr.title,
            state=pr.state,
            merged=pr.merged,
            draft=bool(pr.draft),
            user=pr.user.login,
            user_avatar=pr.user.avatar_url,
            author_association=pr.author_association,
            merged_by=pr.merged_by and pr.merged_by.login,
            commits=pr.commits,
            base_owner=pr.base.repo.owner.login,
            base_label=pr.base.label,
            base_ref=pr.base.ref,
            head_owner=pr.head.repo and pr.head.repo.owner.login,
            head_label=pr.head.label or pr.head.ref,
            head_ref=pr.head.ref,
            merged_at=pr.merged_at,
            created_at=pr.created_at,
            body_html=b if (b := getattr(issue, "body_html", None)) else None,
            body=issue.body if issue.body else None,
            reactions=(
                get_comment_reactions(issue.reactions) if issue.reactions else {}
            ),
        )

    @classmethod
    def from_webhook(cls, pr: models.PullRequestWebhook) -> Self:
        return cls(
            number=pr.number,
            title=pr.title,
            state=pr.state,
            merged=pr.merged,
            draft=bool(pr.draft),
            user=pr.user.login,
            user_avatar=pr.user.avatar_url,
            author_association=pr.author_association,
            merged_by=pr.merged_by and pr.merged_by.login,
            commits=pr.commits,
            base_owner=pr.base.repo.owner.login,
            base_label=pr.base.label,
            base_ref=pr.base.ref,
            head_owner=pr.head.repo and pr.head.repo.owner.login,
            head_label=pr.head.label or pr.head.ref,
            head_ref=pr.head.ref,
            merged_at=pr.merged_at,
            created_at=pr.created_at,
            body_html=None,
            body=pr.body,
            reactions={},
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventAddedToProject:
    event: Literal["added_to_project"]
    actor: str
    actor_avatar: str
    created_at: datetime
    column_name: str | None

    @classmethod
    def from_event(cls, event: models.AddedToProjectIssueEvent) -> Self:
        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            column_name=event.project_card.column_name if event.project_card else None,
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventAssigned:
    event: Literal["assigned"]
    actor: str
    actor_avatar: str
    created_at: datetime
    assignee: str
    assignee_avatar: str

    @classmethod
    def from_event(cls, event: models.TimelineAssignedIssueEvent) -> Self:
        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            assignee=event.assignee.login,
            assignee_avatar=event.assignee.avatar_url,
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventCommented:
    event: Literal["commented"]
    id: int
    actor: str
    actor_avatar: str
    created_at: datetime

    body_html: str | None
    body: str | None
    author_association: str
    reactions: dict[str, int]

    @classmethod
    def from_event(cls, event: models.TimelineCommentEvent) -> Self:
        return cls(
            event=event.event,
            id=event.id,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=event.created_at,
            body_html=event.body_html if event.body_html else None,
            body=event.body if event.body else None,
            author_association=event.author_association,
            reactions=(
                get_comment_reactions(event.reactions) if event.reactions else {}
            ),
        )

    @classmethod
    def from_webhook(
        cls,
        event: (
            models.WebhookIssueCommentCreatedPropComment | models.WebhooksIssueComment
        ),
    ) -> Self:
        return cls(
            event="commented",
            id=event.id,
            actor=event.user.login if event.user else "ghost",
            actor_avatar=(
                event.user.avatar_url
                if event.user and event.user.avatar_url
                else "https://github.com/ghost.png"
            ),
            created_at=event.created_at,
            body_html=None,
            body=event.body,
            author_association=event.author_association,
            reactions=get_comment_reactions(event.reactions),
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventCommitted:
    event: Literal["committed"]
    message: str
    sha: str
    verified: bool

    @classmethod
    def from_event(cls, event: models.TimelineCommittedEvent) -> Self:
        return cls(
            event="committed",
            message=event.message,
            sha=event.sha,
            verified=event.verification.verified,
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventCrossReferenced:
    event: Literal["cross-referenced"]
    actor: str
    actor_avatar: str
    created_at: datetime
    source: IssueInfo | PullRequestInfo | None
    source_repo_full_name: str | None

    @property
    def source_is_pull_request(self) -> bool:
        return isinstance(self.source, PullRequestInfo)

    @classmethod
    async def from_event(
        cls, bot: GitHubBot | OAuthBot, event: models.TimelineCrossReferencedEvent
    ) -> Self:
        if event.source.issue and (
            pull_request := await get_pull_request_from_issue(bot, event.source.issue)
        ):
            source = PullRequestInfo.from_pr(event.source.issue, pull_request)
        elif event.source.issue:
            source = IssueInfo.from_issue(event.source.issue)
        else:
            source = None

        return cls(
            event=event.event,
            actor=event.actor.login if event.actor else "ghost",
            actor_avatar=(
                event.actor.avatar_url
                if event.actor
                else "https://github.com/ghost.png"
            ),
            created_at=event.created_at,
            source=source,
            source_repo_full_name=(
                event.source.issue.repository.full_name
                if event.source.issue and event.source.issue.repository
                else None
            ),
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventDemilestoned:
    event: Literal["demilestoned"]
    actor: str
    actor_avatar: str
    created_at: datetime
    milestone: str

    @classmethod
    def from_event(cls, event: models.DemilestonedIssueEvent) -> Self:
        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            milestone=event.milestone.title,
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventLabeled:
    event: Literal["labeled"]
    actor: str
    actor_avatar: str
    created_at: datetime
    label_name: str
    label_color: tuple[int, int, int, int, int, int]

    @classmethod
    def from_event(cls, event: models.LabeledIssueEvent) -> Self:
        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            label_name=event.label.name,
            label_color=get_issue_label_color(event.label.color),
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventLocked:
    event: Literal["locked"]
    actor: str
    actor_avatar: str
    created_at: datetime
    lock_reason: str | None

    @classmethod
    def from_event(cls, event: models.LockedIssueEvent) -> Self:
        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            lock_reason=event.lock_reason,
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventMilestoned:
    event: Literal["milestoned"]
    actor: str
    actor_avatar: str
    created_at: datetime
    milestone: str

    @classmethod
    def from_event(cls, event: models.MilestonedIssueEvent) -> Self:
        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            milestone=event.milestone.title,
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventMoveColumnInProject:
    event: Literal["moved_columns_in_project"]
    actor: str
    actor_avatar: str
    created_at: datetime
    column_name: str | None
    previous_column_name: str | None

    @classmethod
    def from_event(cls, event: models.MovedColumnInProjectIssueEvent) -> Self:
        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            column_name=event.project_card.column_name if event.project_card else None,
            previous_column_name=(
                event.project_card.previous_column_name
                if event.project_card and event.project_card.previous_column_name
                else None
            ),
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventRemovedFromProject:
    event: Literal["removed_from_project"]
    actor: str
    actor_avatar: str
    created_at: datetime
    column_name: str | None

    @classmethod
    def from_event(cls, event: models.RemovedFromProjectIssueEvent) -> Self:
        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            column_name=event.project_card.column_name if event.project_card else None,
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventRenamed:
    event: Literal["renamed"]
    actor: str
    actor_avatar: str
    created_at: datetime
    from_name: str
    to_name: str

    @classmethod
    def from_event(cls, event: models.RenamedIssueEvent) -> Self:
        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            from_name=event.rename.from_,
            to_name=event.rename.to,
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventReviewDismissed:
    event: Literal["review_dismissed"]
    actor: str
    actor_avatar: str
    created_at: datetime
    dismissal_commit: str | None
    dismissed_review_id: int | None

    @classmethod
    def from_event(cls, event: models.ReviewDismissedIssueEvent) -> Self:
        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            dismissal_commit=(
                event.dismissed_review.dismissal_commit_id
                if event.dismissed_review.dismissal_commit_id
                else None
            ),
            dismissed_review_id=event.dismissed_review.review_id,
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventReviewRequestRemoved:
    event: Literal["review_request_removed"]
    actor: str
    actor_avatar: str
    created_at: datetime
    requested_name: str | None

    @classmethod
    def from_event(cls, event: models.ReviewRequestRemovedIssueEvent) -> Self:
        if event.requested_reviewer:
            requested_name = event.requested_reviewer.login
        elif event.requested_team:
            requested_name = event.requested_team.name
        else:
            requested_name = None

        return cls(
            event=event.event,
            actor=event.review_requester.login,
            actor_avatar=event.review_requester.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            requested_name=requested_name,
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventReviewRequested:
    event: Literal["review_requested"]
    actor: str
    actor_avatar: str
    created_at: datetime
    requested_name: str | None

    @classmethod
    def from_event(cls, event: models.ReviewRequestedIssueEvent) -> Self:
        if event.requested_reviewer:
            requested_name = event.requested_reviewer.login
        elif event.requested_team:
            requested_name = event.requested_team.name
        else:
            requested_name = None

        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            requested_name=requested_name,
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventReviewed:
    event: Literal["reviewed"]
    id: int
    actor: str
    actor_avatar: str
    created_at: datetime | None
    state: str
    body_html: str | None
    body: str | None
    author_association: str

    @classmethod
    def from_event(cls, event: models.TimelineReviewedEvent) -> Self:
        return cls(
            event=event.event,
            id=event.id,
            actor=event.user.login,
            actor_avatar=event.user.avatar_url,
            created_at=event.submitted_at if event.submitted_at else None,
            state=event.state,
            body_html=event.body_html if event.body_html else None,
            body=event.body if event.body else None,
            author_association=event.author_association,
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventUnassigned:
    event: Literal["unassigned"]
    actor: str
    actor_avatar: str
    created_at: datetime
    assignee: str
    assignee_avatar: str

    @classmethod
    def from_event(cls, event: models.TimelineUnassignedIssueEvent) -> Self:
        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            assignee=event.assignee.login,
            assignee_avatar=event.assignee.avatar_url,
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventUnlabeled:
    event: Literal["unlabeled"]
    actor: str
    actor_avatar: str
    created_at: datetime
    label_name: str
    label_color: tuple[int, int, int, int, int, int]

    @classmethod
    def from_event(cls, event: models.UnlabeledIssueEvent) -> Self:
        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            label_name=event.label.name,
            label_color=get_issue_label_color(event.label.color),
        )


@dataclass(frozen=True, kw_only=True)
class TimelineEventStateChange:
    event: str
    actor: str
    actor_avatar: str
    created_at: datetime
    state_reason: str | None
    commit_id: str | None

    @classmethod
    def from_event(cls, event: models.StateChangeIssueEvent) -> Self:
        return cls(
            event=event.event,
            actor=event.actor.login,
            actor_avatar=event.actor.avatar_url,
            created_at=datetime.strptime(event.created_at, "%Y-%m-%dT%H:%M:%SZ"),
            state_reason=event.state_reason if event.state_reason else None,
            commit_id=event.commit_id,
        )


TimelineEvent: TypeAlias = (
    TimelineEventAddedToProject
    | TimelineEventAssigned
    | TimelineEventCommented
    | TimelineEventCommitted
    | TimelineEventCrossReferenced
    | TimelineEventDemilestoned
    | TimelineEventLabeled
    | TimelineEventLocked
    | TimelineEventMilestoned
    | TimelineEventMoveColumnInProject
    | TimelineEventRemovedFromProject
    | TimelineEventRenamed
    | TimelineEventReviewDismissed
    | TimelineEventReviewRequestRemoved
    | TimelineEventReviewRequested
    | TimelineEventReviewed
    | TimelineEventUnassigned
    | TimelineEventUnlabeled
    | TimelineEventStateChange
)


class _MonthInfo(TypedDict):
    month: int
    weeks: int


@dataclass(frozen=True, kw_only=True)
class UserContributionContext:
    username: str
    user_avatar: str
    from_date: date
    to_date: date
    total_contributions: int
    total_commit_contributions: int
    total_issue_contributions: int
    total_pull_request_contributions: int
    total_pull_request_review_contributions: int
    # used to render the calendar header
    month_headers: list[tuple[str, int]]
    # levels of contributions for each day of the week
    day_levels: list[list[int | None]]

    @staticmethod
    def _level_to_int(level: str) -> int:
        if level == "NONE":
            return 0
        elif level == "FIRST_QUARTILE":
            return 1
        elif level == "SECOND_QUARTILE":
            return 2
        elif level == "THIRD_QUARTILE":
            return 3
        elif level == "FOURTH_QUARTILE":
            return 4
        else:
            return 0

    @staticmethod
    def _month_to_name(month: int) -> str:
        return date(2000, month, 1).strftime("%b")

    @classmethod
    def _parse_week(cls, week: list[tuple[str, date]]) -> list[int | None]:
        date_map = {d: cls._level_to_int(lvl) for lvl, d in week}
        # make sunday as the first day of the week
        # calculate the last day of the week to avoid date overflow error
        last_day_of_week = week[-1][1] + timedelta(
            days=6 - week[-1][1].isoweekday() % 7
        )

        def _get_date_contribute(delta: timedelta) -> int | None:
            try:
                return date_map.get(last_day_of_week - delta, None)
            except OverflowError:
                return None

        return [_get_date_contribute(timedelta(days=i)) for i in range(6, -1, -1)]

    @classmethod
    def _parse_month(cls, weeks: list[list[tuple[str, date]]]) -> list[tuple[str, int]]:
        result: list[_MonthInfo] = []
        for week in weeks:
            month = week[0][1].month
            if result and result[-1]["month"] == month:
                result[-1]["weeks"] += 1
            else:
                result.append({"month": month, "weeks": 1})

        return [(cls._month_to_name(info["month"]), info["weeks"]) for info in result]

    @classmethod
    def from_user_contribution(
        cls,
        username: str,
        user_avatar: str,
        total_contributions: int,
        total_commit_contributions: int,
        total_issue_contributions: int,
        total_pull_request_contributions: int,
        total_pull_request_review_contributions: int,
        weeks: list[list[tuple[str, date]]],
    ) -> Self:
        parsed_weeks = [cls._parse_week(week) for week in weeks]
        return cls(
            username=username,
            user_avatar=user_avatar,
            from_date=weeks[0][0][1],
            to_date=weeks[-1][-1][1],
            total_contributions=total_contributions,
            total_commit_contributions=total_commit_contributions,
            total_issue_contributions=total_issue_contributions,
            total_pull_request_contributions=total_pull_request_contributions,
            total_pull_request_review_contributions=total_pull_request_review_contributions,
            month_headers=cls._parse_month(weeks),
            day_levels=[[week[i] for week in parsed_weeks] for i in range(7)],
        )


@dataclass(frozen=True, kw_only=True)
class ReadmeContext:
    repo: RepoInfo
    content: str

    @classmethod
    async def from_repo_readme(
        cls, bot: GitHubBot | OAuthBot, repo: models.FullRepository, content: str
    ) -> Self:
        return cls(
            repo=RepoInfo.from_repo(repo),
            content=content,
        )


@dataclass(frozen=True, kw_only=True)
class IssueContext:
    repo: RepoInfo
    issue: IssueInfo | PullRequestInfo
    timeline_events: list[TimelineEvent]
    highlight_comment: int | None

    @property
    def is_pull_request(self) -> bool:
        return isinstance(self.issue, PullRequestInfo)

    @classmethod
    async def from_issue(
        cls,
        bot: GitHubBot | OAuthBot,
        issue: models.Issue,
        highlight_comment: int | None = None,
    ) -> Self:
        repo = await get_repo_from_issue(bot, issue)

        if pull_request := await get_pull_request_from_issue(bot, issue):
            issue_info = PullRequestInfo.from_pr(issue, pull_request)
        else:
            issue_info = IssueInfo.from_issue(issue)

        timeline_events: list[TimelineEvent] = []
        async for event in bot.github.paginate(
            bot.rest.issues.async_list_events_for_timeline,
            owner=repo.owner.login,
            repo=repo.name,
            issue_number=issue.number,
        ):
            if isinstance(event, models.AddedToProjectIssueEvent):
                timeline_events.append(TimelineEventAddedToProject.from_event(event))
            elif isinstance(event, models.TimelineAssignedIssueEvent):
                timeline_events.append(TimelineEventAssigned.from_event(event))
            elif isinstance(event, models.TimelineCommentEvent):
                timeline_events.append(TimelineEventCommented.from_event(event))
            elif isinstance(event, models.TimelineCommittedEvent):
                timeline_events.append(TimelineEventCommitted.from_event(event))
            elif isinstance(event, models.TimelineCrossReferencedEvent):
                timeline_events.append(
                    await TimelineEventCrossReferenced.from_event(bot, event)
                )
            elif isinstance(event, models.DemilestonedIssueEvent):
                timeline_events.append(TimelineEventDemilestoned.from_event(event))
            elif isinstance(event, models.LabeledIssueEvent):
                timeline_events.append(TimelineEventLabeled.from_event(event))
            elif isinstance(event, models.LockedIssueEvent):
                timeline_events.append(TimelineEventLocked.from_event(event))
            elif isinstance(event, models.MilestonedIssueEvent):
                timeline_events.append(TimelineEventMilestoned.from_event(event))
            elif isinstance(event, models.MovedColumnInProjectIssueEvent):
                timeline_events.append(
                    TimelineEventMoveColumnInProject.from_event(event)
                )
            elif isinstance(event, models.RemovedFromProjectIssueEvent):
                timeline_events.append(
                    TimelineEventRemovedFromProject.from_event(event)
                )
            elif isinstance(event, models.RenamedIssueEvent):
                timeline_events.append(TimelineEventRenamed.from_event(event))
            elif isinstance(event, models.ReviewDismissedIssueEvent):
                timeline_events.append(TimelineEventReviewDismissed.from_event(event))
            elif isinstance(event, models.ReviewRequestRemovedIssueEvent):
                timeline_events.append(
                    TimelineEventReviewRequestRemoved.from_event(event)
                )
            elif isinstance(event, models.ReviewRequestedIssueEvent):
                timeline_events.append(TimelineEventReviewRequested.from_event(event))
            elif isinstance(event, models.TimelineReviewedEvent):
                timeline_events.append(TimelineEventReviewed.from_event(event))
            elif isinstance(event, models.TimelineUnassignedIssueEvent):
                timeline_events.append(TimelineEventUnassigned.from_event(event))
            elif isinstance(event, models.UnlabeledIssueEvent):
                timeline_events.append(TimelineEventUnlabeled.from_event(event))
            elif isinstance(event, models.StateChangeIssueEvent):
                timeline_events.append(TimelineEventStateChange.from_event(event))
            else:
                event_data = event.model_dump(exclude_unset=True)
                logger.debug(f"Unhandled event: {event_data}")
                logger.error(
                    "Unhandled event type: {event_type}",
                    event_type=f"{event.__class__.__name__}"
                    + (
                        f" {event_name}"
                        if (event_name := getattr(event, "event", None))
                        else ""
                    ),
                    event=event_data,
                )

        return cls(
            repo=RepoInfo.from_repo(repo),
            issue=issue_info,
            timeline_events=timeline_events,
            highlight_comment=highlight_comment,
        )


@dataclass(frozen=True, kw_only=True)
class DiffContext:
    repo: RepoInfo
    pr: PullRequestInfo
    diff: str

    @property
    def patch_set(self) -> PatchSet:
        return PatchSet.from_string(self.diff)

    @classmethod
    async def from_issue(cls, bot: GitHubBot | OAuthBot, issue: models.Issue) -> Self:
        repo = await get_repo_from_issue(bot, issue)

        pr = await get_pull_request_from_issue(bot, issue)
        if not pr:
            raise ValueError("Issue is not a pull request")

        diff = await get_diff_from_pull_request(bot, pr)

        return cls(
            repo=RepoInfo.from_repo(repo),
            pr=PullRequestInfo.from_pr(issue, pr),
            diff=diff,
        )


@dataclass(frozen=True, kw_only=True)
class IssueOpenedContext:
    repo: RepoInfo
    issue: IssueInfo | PullRequestInfo
    labels: list[tuple[str, tuple[int, int, int, int, int, int]]]

    @property
    def is_pull_request(self) -> bool:
        return isinstance(self.issue, PullRequestInfo)

    @classmethod
    async def from_webhook(
        cls,
        bot: GitHubBot | OAuthBot,
        repo: models.RepositoryWebhooks,
        issue: models.WebhookIssuesOpenedPropIssue | models.PullRequestWebhook,
    ) -> Self:
        if isinstance(issue, models.PullRequestWebhook):
            issue_info = PullRequestInfo.from_webhook(issue)
        else:
            issue_info = IssueInfo.from_webhook(issue)

        labels: list[tuple[str, tuple[int, int, int, int, int, int]]] = []
        if issue.labels:
            for label in issue.labels:
                labels.append((label.name, get_issue_label_color(label.color)))

        return cls(repo=RepoInfo.from_webhook(repo), issue=issue_info, labels=labels)


@dataclass(frozen=True, kw_only=True)
class IssueCommentedContext:
    repo: RepoInfo
    issue: IssueInfo | PullRequestInfo
    comment: TimelineEventCommented

    @property
    def is_pull_request(self) -> bool:
        return isinstance(self.issue, PullRequestInfo)

    @classmethod
    async def from_webhook(
        cls,
        bot: GitHubBot | OAuthBot,
        repo: models.RepositoryWebhooks,
        issue: (
            models.WebhookIssueCommentCreatedPropIssue
            | models.WebhookIssueCommentEditedPropIssue
        ),
        comment: (
            models.WebhookIssueCommentCreatedPropComment | models.WebhooksIssueComment
        ),
    ) -> Self:
        if pull_request := await get_pull_request_from_issue(bot, issue):
            issue_info = PullRequestInfo.from_pr(issue, pull_request)
        else:
            issue_info = IssueInfo.from_webhook(issue)

        return cls(
            repo=RepoInfo.from_webhook(repo),
            issue=issue_info,
            comment=TimelineEventCommented.from_webhook(comment),
        )


@dataclass(frozen=True, kw_only=True)
class IssueClosedContext:
    repo: RepoInfo
    issue: IssueInfo | PullRequestInfo
    labels: list[tuple[str, tuple[int, int, int, int, int, int]]]
    event: TimelineEventStateChange

    @property
    def is_pull_request(self) -> bool:
        return isinstance(self.issue, PullRequestInfo)

    @classmethod
    async def from_webhook(
        cls,
        bot: GitHubBot | OAuthBot,
        repo: models.RepositoryWebhooks,
        issue: models.WebhookIssuesClosedPropIssue | models.PullRequestWebhook,
        sender: models.SimpleUserWebhooks,
    ) -> Self:
        if isinstance(issue, models.PullRequestWebhook):
            issue_info = PullRequestInfo.from_webhook(issue)
            state_reason = None
            merge_commit_sha = issue.merge_commit_sha
        else:
            issue_info = IssueInfo.from_webhook(issue)
            state_reason = issue.state_reason if issue.state_reason else None
            merge_commit_sha = None

        labels: list[tuple[str, tuple[int, int, int, int, int, int]]] = []
        if issue.labels:
            for label in issue.labels:
                labels.append((label.name, get_issue_label_color(label.color)))

        return cls(
            repo=RepoInfo.from_webhook(repo),
            issue=issue_info,
            labels=labels,
            event=TimelineEventStateChange(
                event="closed",
                actor=sender.login,
                actor_avatar=sender.avatar_url,
                created_at=issue.closed_at or issue.updated_at,
                state_reason=state_reason,
                commit_id=merge_commit_sha,
            ),
        )
