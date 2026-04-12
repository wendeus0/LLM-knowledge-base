from kb.jobs import get_job_catalog, list_jobs


def test_job_catalog_should_use_discover_category_for_known_jobs():
    catalog = get_job_catalog()

    assert catalog["compile"].category == "pipeline"
    assert catalog["lint"].category == "maintenance"
    assert catalog["metrics"].category == "operations"
    assert catalog["decay"].category == "maintenance"
    assert catalog["contradiction-check"].category == "maintenance"
    assert catalog["index-refresh"].category == "pipeline"
    assert catalog["health"].category == "operations"


def test_list_jobs_should_include_category_metadata():
    jobs = list_jobs()

    job_map = {job.name: job for job in jobs}
    assert job_map["compile"].category == "pipeline"
    assert job_map["lint"].category == "maintenance"
    assert job_map["review"].category == "maintenance"
    assert job_map["metrics"].category == "operations"
    assert job_map["decay"].category == "maintenance"
    assert job_map["contradiction-check"].category == "maintenance"
    assert job_map["index-refresh"].category == "pipeline"
    assert job_map["health"].category == "operations"
