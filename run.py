import json
import argparse
import os

# import requests


def run():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('repo-token', help='an integer for the accumulator')
    args = parser.parse_args()
    print(args)
    github_event_path = os.environ['GITHUB_EVENT_PATH']

    # gitbhub_token = os.environ['GITHUB_TOKEN']

    with open(github_event_path, 'rb') as f:
        github_event = json.loads(f)

    print(github_event)

    print()
    print()

    print(os.environ)


if __name__ == '__main__':
    run()

# return unless github_event['action'] == 'created'
#
# body = File.read('/github/workspace/action-add-qa-message/qa_list.md')
#
# github_token = ENV['GITHUB_TOKEN']
# api_version = 'v3'
# header = {
#   'Accept': "application/vnd.github.#{api_version}+json",
#   'Authorization': "token #{github_token}"
# }
#
# issue_number = github_event['issue']['number']
# repo = ENV['GITHUB_REPOSITORY']
#
# uri = URI.parse("https://api.github.com/repos/#{repo}/issues/#{issue_number}/comments")
#
# http = Net::HTTP.new(uri.host, uri.port)
# http.use_ssl = true
# request = Net::HTTP::Post.new(uri.request_uri, header)
# request.body = { body: body }.to_json
#
# http.request(request)
