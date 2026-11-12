import argparse
import sys
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.data_generator.generator import ManufacturingDataGenerator, DEFAULT_SEED

def main():
    parser = argparse.ArgumentParser(description="FactoryPulse Synthetic Data Generator")
    parser.add_argument("--mode", choices=["starter", "full"], default="starter", help="Dataset mode (starter or full)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Reproducible random seed (default: 20261022)")
    parser.add_argument("--export-dir", type=str, default="data", help="Output directory for ground truth and exports")
    parser.add_argument("--no-clean", dest="clean", action="store_false", default=True, help="Do not drop existing tables before generating")
    args = parser.parse_args()

    print("================================================================================")
    print(" FACTORYPULSE SYNTHETIC DATASET GENERATOR")
    print(f" Mode: {args.mode.upper()} | Seed: {args.seed} | Export Dir: {args.export_dir}")
    print("================================================================================")

    generator = ManufacturingDataGenerator(seed=args.seed, mode=args.mode, clean=args.clean)
    generator.run(export_dir=args.export_dir)
    print("Data generation complete!")

if __name__ == "__main__":
    main()
