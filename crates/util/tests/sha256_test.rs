/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use fapolicy_util::sha::sha256_digest;
use std::fs::File;
use std::io::BufReader;

#[test]
fn test_hashme() {
    let expected = "047bc85db1001a7c98c13f594178d339efc60e3b099af5d27a65498ddc808f55";
    let f = File::open("tests/data/hashme.txt").expect("failed to open file");
    let actual = sha256_digest(BufReader::new(&f)).expect("failed to hash file");
    assert_eq!(actual, expected);
}
