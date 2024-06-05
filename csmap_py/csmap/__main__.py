from csmap.process import CsmapParams, process


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input_dem_path", type=str, help="input DEM path")
    parser.add_argument("output_path", type=str, help="output path")
    parser.add_argument(
        "--chunk_size",
        type=int,
        default=1024,
        help="chunk size as pixel, default to 1024",
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=1,
        help="max workers for multiprocessing, default to 1",
    )
    parser.add_argument(
        "--gf_size", type=int, default=12, help="gaussian filter size, default to 12"
    )
    parser.add_argument(
        "--gf_sigma", type=int, default=3, help="gaussian filter sigma, default to 3"
    )
    parser.add_argument(
        "--curvature_size",
        type=int,
        default=1,
        help="curvature filter size, default to 1",
    )
    parser.add_argument(
        "--height_scale",
        type=float,
        nargs=2,
        default=[0.0, 1000.0],
        help="height scale, min max, default to 0.0 1000.0",
    )
    parser.add_argument(
        "--slope_scale",
        type=float,
        nargs=2,
        default=[0.0, 1.5],
        help="slope scale, min max, default to 0.0 1.5",
    )
    parser.add_argument(
        "--curvature_scale",
        type=float,
        nargs=2,
        default=[-0.1, 0.1],
        help="curvature scale, min max, default to -0.1 0.1",
    )

    args = parser.parse_args()

    params = CsmapParams(
        gf_size=args.gf_size,
        gf_sigma=args.gf_sigma,
        curvature_size=args.curvature_size,
        height_scale=args.height_scale,
        slope_scale=args.slope_scale,
        curvature_scale=args.curvature_scale,
    )

    return {
        "input_dem_path": args.input_dem_path,
        "output_path": args.output_path,
        "chunk_size": args.chunk_size,
        "max_workers": args.max_workers,
        "params": params,
    }


def main():
    args = parse_args()
    process(**args)


if __name__ == "__main__":
    main()
