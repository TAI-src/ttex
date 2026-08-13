from ttex.xp_log.event.environment_events import (
    EnvironmentClose,
    EnvironmentInit,
    EnvironmentReset,
    EnvironmentStep,
    EnvironmentEvent,
)


def test_env_init():
    env_init = EnvironmentInit(
        exp_id="test_exp_id",
        alg_id="test_alg_id",
        config={"param1": "value1"},
        kwargs={"arg1": "valueA"},
    )
    assert isinstance(env_init, EnvironmentEvent)
    assert env_init.exp_id == "test_exp_id"
    assert env_init.alg_id == "test_alg_id"
    assert isinstance(env_init.id, str) and len(env_init.id) > 0


def test_env_close():
    env_close = EnvironmentClose(exp_id="test_exp_id", alg_id="test_alg_id")
    assert isinstance(env_close, EnvironmentEvent)
    assert env_close.exp_id == "test_exp_id"
    assert env_close.alg_id == "test_alg_id"


def test_env_step():
    observation = {"state": [0.1, 0.2, 0.3]}
    reward = 1.0
    trunc = False
    term = False
    info = {"info_key": "info_value"}
    env_step = EnvironmentStep(
        exp_id="test_exp_id",
        alg_id="test_alg_id",
        observation=observation,
        reward=reward,
        trunc=trunc,
        term=term,
        info=info,
    )
    assert isinstance(env_step, EnvironmentEvent)
    assert env_step.exp_id == "test_exp_id"
    assert env_step.alg_id == "test_alg_id"
    assert env_step.observation == observation
    assert env_step.reward == reward
    assert env_step.trunc == trunc
    assert env_step.term == term
    assert env_step.info == info


def test_env_reset():
    observation = {"state": [0.1, 0.2, 0.3]}
    seed = 42
    env_reset = EnvironmentReset(
        exp_id="test_exp_id",
        alg_id="test_alg_id",
        observation=observation,
        seed=seed,
    )
    assert isinstance(env_reset, EnvironmentEvent)
    assert env_reset.exp_id == "test_exp_id"
    assert env_reset.alg_id == "test_alg_id"
    assert env_reset.observation == observation
    assert env_reset.seed == seed
