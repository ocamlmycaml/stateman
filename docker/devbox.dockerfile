ARG DOCKER_REGISTRY=${DOCKER_REGISTRY:-artifactory.service.bo1.csnzoo.com}
ARG BASE_OS=${BASE_OS:-centos73}
FROM ${DOCKER_REGISTRY}/wayfair/python/${BASE_OS}-devbox:0.2.0

RUN /pyenv/versions/stateman/bin/pip install --only-binary :all -r requirements-test.txt

