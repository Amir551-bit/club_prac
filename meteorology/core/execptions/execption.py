from fastapi import HTTPException, status


def raise_not_found(detail: str = "object not found"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=detail)


def raise_bad_request(detail: str = "object has problem"):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail=detail)


def raise_forbidden(detail: str = "object is problem"):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail=detail)

