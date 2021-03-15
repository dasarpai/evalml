from evalml.automl.engine.engine_base import (
    EngineBase,
    EngineComputation,
    evaluate_pipeline,
    train_pipeline
)
from evalml.objectives.utils import get_objective


class SequentialComputation(EngineComputation):

    def __init__(self, work, **kwargs):
        self.work = work
        self.kwargs = kwargs
        self.meta_data = {}

    def done(self) -> bool:
        return True

    def get_result(self):
        return self.work(**self.kwargs)

    def cancel(self) -> None:
        return


class SequentialEngine(EngineBase):
    """The default engine for the AutoML search. Trains and scores pipelines locally, one after another."""

    def submit_evaluation_job(self, automl_data, pipeline) -> EngineComputation:
        logger = self.setup_job_log()
        return SequentialComputation(work=evaluate_pipeline,
                                     pipeline=pipeline,
                                     automl_data=automl_data, X=automl_data.X_train,
                                     y=automl_data.y_train,
                                     logger=logger)

    def submit_training_job(self, automl_data, pipeline) -> EngineComputation:
        return SequentialComputation(work=train_pipeline,
                                     pipeline=pipeline, X=automl_data.X_train,
                                     y=automl_data.y_train,
                                     optimize_thresholds=automl_data.optimize_thresholds,
                                     objective=automl_data.objective)

    def submit_scoring_job(self, automl_data, pipeline, X, y, objectives):
        objectives = [get_objective(o, return_instance=True) for o in objectives]
        computation = SequentialComputation(work=pipeline.score,
                                            X=X, y=y, objectives=objectives)
        computation.meta_data["pipeline_name"] = pipeline.name
        return computation
