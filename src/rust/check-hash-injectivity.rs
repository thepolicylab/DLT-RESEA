use rust_decimal::{Decimal, RoundingStrategy};
use rust_decimal::prelude::*;
use core::str::FromStr;
use std::thread;
use std::convert::TryInto;
use std::collections::BinaryHeap;


fn pct_along(num: i64, den: i64, min_val: i64, max_val: i64) -> i64 {
    let numf = num as f64;
    let denf = den as f64;
    let min_valf = min_val as f64;
    let max_valf = max_val as f64;

    return (numf / denf * (max_valf - min_valf) + min_valf) as i64;
}

/// This function enumerates all possible social security numbers and runs them through
/// the "hashing" algorithm. The question is whether we actually get an honest _shuffle_
/// and not just a hash with collisions.
///
/// There's probably a better way to do this, to be honest, but this is essentially
/// a merge+heapsort that's doing everything in memory. It takes quite a bit of memory
/// (like 6GB); and it takes quite a bit of time (probably because I'm
/// pop-ing in the heaps instead of drain_sorted-ing, but that's an unstable feature
/// and I don't want to install a nightly build).
fn main() {
    let num_threads: i64 = 10;
    let min_ssn: i64 = 1;
    let max_ssn: i64 = 1_000_000_000;

    let mut handles = Vec::with_capacity(num_threads.try_into().unwrap());

    for num_thread in 0..num_threads {
        let zero = Decimal::from_str("0").unwrap();
        let one = Decimal::from_str("1").unwrap();
        let mut ca = Decimal::from_str("16807").unwrap();
        ca.rescale(10);
        let mut cm = Decimal::from_str("2147483647").unwrap();
        cm.rescale(10);
        let mut cq = Decimal::from_str("127773").unwrap();
        cq.rescale(10);
        let mut cr = Decimal::from_str("2836").unwrap();
        cr.rescale(10);

        handles.push(
           thread::spawn(move || {
                let min_val = pct_along(num_thread, num_threads, min_ssn, max_ssn);
                let max_val = pct_along(num_thread + 1, num_threads, min_ssn, max_ssn);
                // let mut hset = HashSet::new();
                let mut heap = BinaryHeap::<u64>::new();
                for i in min_val..max_val {
                    if i % 1_000_000 == 0 {
                        println!("On thread {} at iteration {} of {}", num_thread, i - min_val, max_val - min_val);
                    }
                    let mut lsd = Decimal::from_i64(i).unwrap();
                    lsd.rescale(10);

                    let mut whi = lsd / cq;
                    whi = whi.round_dp_with_strategy(0, RoundingStrategy::ToZero);
                    whi.rescale(10);
                    let mut wlo = lsd - cq * whi;
                    wlo.rescale(10);
                    lsd = ca * wlo - cr * whi;

                    if lsd <= zero {
                        lsd = lsd + cm;
                    }
                    let mut lrand = lsd / cm;
                    lrand = lrand.round_dp_with_strategy(10, RoundingStrategy::ToZero);
                    let mantissa = lrand.mantissa();

                    // Assert that the result is actually between 0 and 1
                    assert!(mantissa >= 0);
                    assert!(lrand <= one);

                    // Then the result is only 10 digits, so won't _quite_ fit into
                    // a u32. We'll keep it in a u64
                    heap.push(mantissa as u64);
                }
                println!("On thread {} found length {}", num_thread, heap.len());
                heap
           })
        );
    }

    // Join all the threads and gather the heaps
    let mut heaps = Vec::with_capacity(num_threads.try_into().unwrap());
    for handle in handles {
        heaps.push(handle.join().unwrap());
    }

    let mut final_heap = BinaryHeap::<(u64, usize)>::new();
    for i in 0..heaps.len() {
        final_heap.push((heaps[i].pop().unwrap(), i));
    }
    let mut last_seen_val_pair = final_heap.pop().unwrap();
    let mut last_seen_val = last_seen_val_pair.0;
    let mut last_seen_val_pos = last_seen_val_pair.1;
    if heaps[last_seen_val_pos].len() > 0 {
        final_heap.push((heaps[last_seen_val_pos].pop().unwrap(), last_seen_val_pos));
    }
    let mut num_identical_vals = 0;
    let mut counter = 1;
    while final_heap.len() > 0 {
        if counter % 10_000_000 == 0 {
            println!("Made it through {} elts", counter);
        }
        last_seen_val_pair = final_heap.pop().unwrap();
        if last_seen_val == last_seen_val_pair.0 {
            num_identical_vals += 1;
        }
        counter += 1;

        last_seen_val = last_seen_val_pair.0;
        last_seen_val_pos = last_seen_val_pair.1;
        if heaps[last_seen_val_pos].len() > 0 {
            final_heap.push((heaps[last_seen_val_pos].pop().unwrap(), last_seen_val_pos));
        }
    }

    println!("Have {} and {}", num_identical_vals, counter);
}
