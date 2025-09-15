# COCO Logger

The COCO Logger is a utility based on the [python logging facility](https://docs.python.org/3/library/logging.html), designed to facilitate outputting logs in the [COCO (COmparing Continuous Optimizers)](https://coco-platform.org/) format. This allows the seamless usage of the COCO post-processing tools for analyzing optimization results ([cocopp](https://pypi.org/project/cocopp/)).

## Usage

Set up a logger object and use it to log the progress using predefined logging events. All events should be logged at the `INFO` level. More details about the events and the required parameters can be found [below](#logging-events).

```python
from ttex.log.coco import COCOStart, COCOEval, COCOEnd, setup_coco_logger

logger = setup_coco_logger(trigger_nth = 2, "coco_logger")
# trigger nth is the frequency of logging, e.g., every 2nd evaluation
# this is in addition to any target-based triggers for logging

logger.info(COCOStart(algo="my_algorithm", ...))  # Log the start of the optimization
logger.info(COCOEval(x=[0.1, 0.2], mf=0.8))  # Log an evaluation
logger.info(COCOEnd())  # Log the end of the optimization
```

In the current example, a folder called my_algorithm is created that contains the required COCO files (`.info`, `.dat`, `.tdat`). Post-processing can then be done by pointing to said folder.

For each problem instance, a separate .info file is created. For each problem, an additional folder is created containing the .dat and .tdat files, one separately for each dimension and instance.[^1]

```bash
python -m cocopp my_algorithm
```

## Logging events

The COCO Logger supports the following logging events:

- `COCOStart`: Logs the start of an optimization run.
- `COCOEval`: Logs an evaluation of the objective function.
- `COCOEnd`: Logs the end of an optimization run.

```python
@dataclass(frozen=True)
class COCOEval(LogEvent):
    x: list[float]  # point in search space
    mf: float  # measured fitness


@dataclass(frozen=True)
class COCOEnd(LogEvent):
    pass


@dataclass(frozen=True)
class COCOStart(LogEvent):
    fopt: float  # optimal fitness value
    algo: str  # algorithm name
    problem: int  # problem id
    dim: int  # search space dimension
    inst: int  # instance id
    suite: str  # suite name
    exp_id: str = str(uuid4())  # experiment id, defaults to random uuid
```

[^1]: Note that this is slightly different from the standard COCO setup, where there is one info file per problem, and .dat/.tdat files typically create multiple instances. We opted for this setup to simplify the logging process. The standard cocopp tools can still be used for post-processing.
