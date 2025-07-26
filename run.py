#!/usr/bin/env python3
"""
Portfolio Coach - Main Entry Point
==================================

This is the main entry point for the Portfolio Coach system.
It provides a unified interface to run different components of the system.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def main():
    """Main entry point for Portfolio Coach."""
    import argparse
    import logging
    
    parser = argparse.ArgumentParser(description="Portfolio Coach System")
    parser.add_argument("--mode", choices=["runner", "web", "test-config"], 
                       default="runner", help="Run mode")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Run in dry-run mode (no actual trades)")
    parser.add_argument("--test-config", action="store_true",
                       help="Test configuration only")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Portfolio Coach System...")
    
    try:
        if args.mode == "web":
            from web.app import app
            logger.info("Starting web interface...")
            app.run(host="0.0.0.0", port=5000, debug=args.debug)
            
        elif args.mode == "test-config" or args.test_config:
            from scripts.portfolio_coach_runner import PortfolioCoachRunner
            runner = PortfolioCoachRunner()
            runner.test_configuration()
            
        else:  # runner mode
            from scripts.portfolio_coach_runner import PortfolioCoachRunner
            runner = PortfolioCoachRunner()
            
            if args.dry_run:
                logger.info("Running in dry-run mode...")
                runner.test_configuration()
            else:
                logger.info("Running full Portfolio Coach pipeline...")
                runner.run_full_pipeline()
                
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all dependencies are installed and paths are correct")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running Portfolio Coach: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
