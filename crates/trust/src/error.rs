use std::io;
use thiserror::Error;

/// An Error that can occur in this crate
#[derive(Error, Debug)]
pub enum Error {
    #[error("lmdb db not found, {0}")]
    LmdbNotFound(String),
    #[error("{0}")]
    LmdbReadFail(lmdb::Error),
    #[error("Permission denied, {0}")]
    LmdbPermissionDenied(String),
    #[error("Unsupported Trust type: {0}")]
    UnsupportedTrustType(String),
    #[error("Malformed Trust entry: {0}")]
    MalformattedTrustEntry(String),
    #[error("{0} file not found at {1}")]
    TrustSourceNotFound(String, String),

    #[error("File IO Error: {0}")]
    FileIoError(#[from] io::Error),

    #[error("Error reading metadata: {0}")]
    MetaError(String),

    #[error("{0}")]
    GeneralError(#[from] fapolicy_util::error::Error),
}