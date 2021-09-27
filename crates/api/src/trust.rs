use serde::Deserialize;
use serde::Serialize;

/// # The definition of Trust
/// - Path to the file
/// - Size of the file
/// - Hash of the file
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Trust {
    pub path: String,
    pub size: u64,
    pub hash: String,
}

impl Trust {
    pub fn new(path: &str, size: u64, hash: &str) -> Trust {
        Trust {
            path: path.to_string(),
            size,
            hash: hash.to_string(),
        }
    }
}