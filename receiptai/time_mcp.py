import asyncio
import calendar
import json
import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union, cast

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Custom type definitions
class DateRange(TypedDict):
    start: str  # ISO format date
    end: str  # ISO format date


def get_today() -> str:
    """Returns today's date in ISO format."""
    return date.today().isoformat()


def get_tomorrow() -> str:
    """Returns tomorrow's date in ISO format."""
    return (date.today() + timedelta(days=1)).isoformat()


def get_next_week() -> DateRange:
    """Returns the start and end dates of next week."""
    today = date.today()
    start_of_next_week = today + timedelta(days=(7 - today.weekday()))
    end_of_next_week = start_of_next_week + timedelta(days=6)
    return {'start': start_of_next_week.isoformat(), 'end': end_of_next_week.isoformat()}


def get_last_week() -> DateRange:
    """Returns the start and end dates of last week."""
    today = date.today()
    start_of_last_week = today - timedelta(days=(today.weekday() + 7))
    end_of_last_week = start_of_last_week + timedelta(days=6)
    return {'start': start_of_last_week.isoformat(), 'end': end_of_last_week.isoformat()}


def get_next_month() -> DateRange:
    """Returns the start and end dates of next month."""
    today = date.today()
    next_month = today.month % 12 + 1
    year = today.year + (today.month == 12)
    first_day_next_month = date(year, next_month, 1)
    month_after = next_month % 12 + 1
    year_after = year + (next_month == 12)
    last_day_next_month = date(year_after, month_after, 1) - timedelta(days=1)
    return {'start': first_day_next_month.isoformat(), 'end': last_day_next_month.isoformat()}


def get_last_month() -> DateRange:
    """Returns the start and end dates of last month."""
    today = date.today()
    last_month = (today.month - 2 + 12) % 12 + 1
    year = today.year - (today.month == 1)
    first_day_last_month = date(year, last_month, 1)
    last_day_last_month = date(today.year, today.month, 1) - timedelta(days=1)
    return {'start': first_day_last_month.isoformat(), 'end': last_day_last_month.isoformat()}


def get_next_year() -> DateRange:
    """Returns the start and end dates of next year."""
    today = date.today()
    next_year = today.year + 1
    return {'start': date(next_year, 1, 1).isoformat(), 'end': date(next_year, 12, 31).isoformat()}


def get_last_year() -> DateRange:
    """Returns the start and end dates of last year."""
    today = date.today()
    last_year = today.year - 1
    return {'start': date(last_year, 1, 1).isoformat(), 'end': date(last_year, 12, 31).isoformat()}


def get_specific_range(start_date_str: str, end_date_str: str) -> DateRange:
    """Returns the start and end dates for a specific range."""
    start_date = date.fromisoformat(start_date_str)
    end_date = date.fromisoformat(end_date_str)
    return {'start': start_date.isoformat(), 'end': end_date.isoformat()}


def get_relative_date(duration: int, unit: Literal['days', 'weeks', 'months']) -> Union[str, None]:
    """Returns a date relative to today based on duration and unit."""
    today = date.today()
    if unit == 'days':
        return (today + timedelta(days=duration)).isoformat()
    elif unit == 'weeks':
        return (today + timedelta(weeks=duration)).isoformat()
    elif unit == 'months':
        month = today.month - 1 + duration
        year = today.year + month // 12
        month = month % 12 + 1
        try:
            return date(year, month, today.day).isoformat()
        except ValueError:
            return date(year, month, calendar.monthrange(year, month)[1]).isoformat()
    return None  # Should not happen if input is validated


def get_past_relative_date(
    duration: int, unit: Literal['days', 'weeks', 'months']
) -> Union[str, None]:
    """Returns a date in the past relative to today based on duration and unit."""
    today = date.today()
    if unit == 'days':
        return (today - timedelta(days=duration)).isoformat()
    elif unit == 'weeks':
        return (today - timedelta(weeks=duration)).isoformat()
    elif unit == 'months':
        month = today.month - 1 - duration
        year = today.year + month // 12
        month = month % 12 + 1
        try:
            return date(year, month, today.day).isoformat()
        except ValueError:
            return date(year, month, calendar.monthrange(year, month)[1]).isoformat()
    return None  # Should not happen if input is validated


async def time_mcp() -> None:
    """Initialize and run the time MCP server"""
    server = Server('time')

    @server.list_prompts()
    async def list_prompts() -> List[types.Prompt]:
        return []

    @server.list_tools()
    async def handle_list_tools() -> List[types.Tool]:
        return [
            types.Tool(
                name='get_date',
                description='Retrieve specific dates or date ranges like today, tomorrow, next week, last week, next month, last month, next year, last year, or a specific date range. Also allows specifying relative dates like "in_3_days" or "last_2_weeks".',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'date_type': {
                            'type': 'string',
                            'enum': [
                                'today',
                                'tomorrow',
                                'next_week',
                                'last_week',
                                'next_month',
                                'last_month',
                                'next_year',
                                'last_year',
                                'specific_range',
                                'in_days',
                                'in_weeks',
                                'in_months',
                                'last_days',
                                'last_weeks',
                                'last_months',
                            ],
                            'description': 'The type of date or date range to retrieve.',
                        },
                        'start_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'Start date for a specific range (YYYY-MM-DD). Required when date_type is "specific_range".',
                        },
                        'end_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'End date for a specific range (YYYY-MM-DD). Required when date_type is "specific_range".',
                        },
                        'duration': {
                            'type': 'integer',
                            'description': 'Number of days, weeks, or months for relative dates. Required when date_type is "in_days", "in_weeks", "in_months", "last_days", "last_weeks", or "last_months".',
                        },
                    },
                    'required': ['date_type'],
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: Optional[Dict[str, Any]]
    ) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        if name == 'get_date':
            if not arguments or 'date_type' not in arguments:
                return [
                    types.TextContent(
                        type='text',
                        text=json.dumps(
                            {'status': 'error', 'error': 'Missing required argument: date_type'},
                            indent=2,
                        ),
                    )
                ]

            response_data: Dict[str, Union[str, DateRange, Dict[str, str], None]] = {
                'status': 'success'
            }
            date_type = cast(str, arguments.get('date_type'))

            try:
                match date_type:
                    case 'today':
                        response_data['today'] = get_today()
                    case 'tomorrow':
                        response_data['tomorrow'] = get_tomorrow()
                    case 'next_week':
                        response_data['next_week'] = get_next_week()
                    case 'last_week':
                        response_data['last_week'] = get_last_week()
                    case 'next_month':
                        response_data['next_month'] = get_next_month()
                    case 'last_month':
                        response_data['last_month'] = get_last_month()
                    case 'next_year':
                        response_data['next_year'] = get_next_year()
                    case 'last_year':
                        response_data['last_year'] = get_last_year()
                    case 'specific_range':
                        if 'start_date' not in arguments or 'end_date' not in arguments:
                            return [
                                types.TextContent(
                                    type='text',
                                    text=json.dumps(
                                        {
                                            'status': 'error',
                                            'error': 'Both start_date and end_date are required for specific_range',
                                        },
                                        indent=2,
                                    ),
                                )
                            ]
                        start_date = cast(str, arguments['start_date'])
                        end_date = cast(str, arguments['end_date'])
                        response_data['specific_range'] = get_specific_range(start_date, end_date)
                    case 'in_days' | 'in_weeks' | 'in_months' as unit_type:
                        if (
                            'duration' not in arguments
                            or not isinstance(arguments['duration'], int)
                            or arguments['duration'] <= 0
                        ):
                            return [
                                types.TextContent(
                                    type='text',
                                    text=json.dumps(
                                        {
                                            'status': 'error',
                                            'error': "A positive integer 'duration' is required for relative date types",
                                        },
                                        indent=2,
                                    ),
                                )
                            ]
                        duration = cast(int, arguments['duration'])
                        unit = cast(Literal['days', 'weeks', 'months'], unit_type.split('_')[1])
                        response_data['in_future'] = get_relative_date(duration, unit)
                    case 'last_days' | 'last_weeks' | 'last_months' as unit_type:
                        if (
                            'duration' not in arguments
                            or not isinstance(arguments['duration'], int)
                            or arguments['duration'] <= 0
                        ):
                            return [
                                types.TextContent(
                                    type='text',
                                    text=json.dumps(
                                        {
                                            'status': 'error',
                                            'error': "A positive integer 'duration' is required for relative date types",
                                        },
                                        indent=2,
                                    ),
                                )
                            ]
                        duration = cast(int, arguments['duration'])
                        unit = cast(Literal['days', 'weeks', 'months'], unit_type.split('_')[1])
                        response_data['in_past'] = get_past_relative_date(duration, unit)
                    case _:
                        return [
                            types.TextContent(
                                type='text',
                                text=json.dumps(
                                    {'status': 'error', 'error': f'Invalid date_type: {date_type}'},
                                    indent=2,
                                ),
                            )
                        ]

                return [
                    types.TextContent(
                        type='text',
                        text=json.dumps(response_data, indent=2),
                    )
                ]
            except ValueError as e:
                return [
                    types.TextContent(
                        type='text', text=json.dumps({'status': 'error', 'error': str(e)}, indent=2)
                    )
                ]
        else:
            return [
                types.TextContent(
                    type='text',
                    text=json.dumps({'status': 'error', 'error': 'invalid tool call'}, indent=2),
                )
            ]

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name='time',
                server_version='0.1.0',
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == '__main__':
    asyncio.run(time_mcp())
