"""Clinic-related API routes (on-demand address lookup)."""

from __future__ import annotations

from fastapi import APIRouter, status

from backend.app.api.schemas import (
    ClinicAddressLookupRequest,
    ClinicAddressLookupResponse,
)
from backend.app.application.clinic_catalog import lookup_address_by_name

router = APIRouter(tags=["Clinics"])


@router.post(
    "/clinics/lookup-address",
    response_model=ClinicAddressLookupResponse,
    status_code=status.HTTP_200_OK,
    summary="Look up a clinic address by name",
    description=(
        "Search for a clinic address given a clinic name. "
        "Uses Nominatim first, then web search fallback (including proxy fallback) "
        "when needed. Response field 'source' indicates which resolver produced "
        "the result, or 'none' when no usable address is found."
    ),
)
def lookup_clinic_address(body: ClinicAddressLookupRequest) -> ClinicAddressLookupResponse:
    result = lookup_address_by_name(body.clinic_name)
    return ClinicAddressLookupResponse(
        found=bool(result.get("found", False)),
        address=result.get("address") if result.get("found") else None,
        source=str(result.get("source", "none")),
    )
