
import sys
import subprocess
import codecs

from gooey import Gooey, GooeyParser

if sys.stdout.encoding != 'UTF-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


@Gooey(
    # language='korean',
    navigation='TABBED',
    optional_cols=1,
    progress_regex=r"reviewing.*\(([\d.]+)%\)$",
    timing_options = {
        'show_time_remaining': True,
        'hide_time_remaining_on_complete': True,
    },
    clear_before_run=True,
)
def main():
    parser = GooeyParser(description='Akochan reviewer GUI')

    subs = parser.add_subparsers(help='options')

    simple_parser = subs.add_parser(
        'Simple', help='Simple options')
    simple_parser_group = simple_parser.add_argument_group()
    simple_parser_group.add_argument('--in-file', metavar='천봉 패보 파일', widget='FileChooser', required=True)
    simple_parser_group.add_argument('--actor', metavar='작사 번호', help='복기 대상 작사 번호. 천봉 패보 링크의 "&tw=" 뒤쪽 숫자입니다.', required=True)
    simple_parser_group.add_argument('--kyokus', metavar='국', help='복기할 국. 지정하지 않을 경우 모든 국을 복기합니다. 예시(동1국, 동4국, 남3국1본장): "E1,E4,S3.1".')
    simple_parser_group.add_argument('--pt', metavar='포인트', help='최종 순위별 포인트 등락. 예시: "90,45,0,-135".', default='75,35,-5,-195')
    simple_parser_group.add_argument('--deviation-threshold', metavar='편차 임계값', help='임계값은 복기 대상 작사의 EV가 [최고 EV - 임계값, 최고 EV]의 범위일 경우 잘못된 판단을 무시하도록 합니다. 레퍼런스 값은 포인트 모드에서는 사용할 경우 0.05, 순위를 사용할 경우 0.001입니다.', default=0.05, widget='DecimalField',gooey_options={
        'min': 0, 
        'increment': 0.001,
    })
    simple_parser_group.add_argument('--lang', metavar='언어', help='복기 페이지를 표시할 때 사용할 언어입니다.', choices=['ja', 'en'], nargs=1, default='en')
    simple_parser_group.add_argument('--akochan-reviewer', metavar='akochan-reviewer.exe 경로', default='.\\akochan-reviewer\\akochan-reviewer.exe', widget='FileChooser', required=True)
    simple_parser_group.add_argument('--akochan-dir', metavar='akochan 디렉터리', default=".\\akochan-reviewer\\akochan", widget='DirChooser')
    simple_parser_group.add_argument('--tactics-config', metavar='전술 설정 파일', default=".\\akochan-reviewer\\tactics.json", widget='FileChooser')
    
    advanced_parser = subs.add_parser(
        'Advanced', help='All available options')
    advanced_parser_group = advanced_parser.add_argument_group()
    advanced_parser_group.add_argument('--akochan-reviewer', help='Path of akochan-reviewer.exe', default='.\\akochan-reviewer\\akochan-reviewer.exe', widget='FileChooser', required=True)
    advanced_parser_group.add_argument('--anonymous', help='Do not include player names.', action='store_true')
    advanced_parser_group.add_argument('--json', help='Output review result in JSON instead of HTML.', action='store_true')
    advanced_parser_group.add_argument('--no-open', help='Do not open the output file in browser after finishing.', action='store_true')
    advanced_parser_group.add_argument('--no-review', help='Do not review at all. Only download and save files.', action='store_true')
    advanced_parser_group.add_argument('--use-placement-ev', help='Use final placement EV instead of pt EV. This will override --pt and \'jun_pt\' in --tactics-config.', action='store_true')
    advanced_parser_group.add_argument('--verbose', help='Use verbose output.', action='store_true')
    advanced_parser_group.add_argument('--without-viewer', help='Do not include log viewer in the generated HTML report.', action='store_true')

    advanced_parser_group.add_argument('--actor', help='Specify the actor to review. It is the number after "&tw=" in tenhou\'s log url.')
    advanced_parser_group.add_argument('--akochan-dir', help='Specify the directory of akochan. This will serve as the working directory of akochan process. Default value "akochan"', default=".\\akochan-reviewer\\akochan", widget='DirChooser')
    advanced_parser_group.add_argument('--deviation-threshold', help='HRESHOLD is an absolute value that the reviewer will ignore all problematic moves whose EVs are within the range of [best EV - THRESHOLD, best EV]. This option is effective under both pt and placement EV mode. It is recommended to use it with --use-placement-ev where the reward distribution is fixed and even. Reference value: 0.05 when using pt and 0.001 when using placement. Default value: "0.001".', default=0.001, widget='DecimalField',gooey_options={
        'min': 0, 
        'increment': 0.001,
    })
    advanced_parser_group.add_argument('--in-file', help='Specify a tenhou.net/6 format log file to review. If FILE is "-" or empty, read from stdin.', widget='FileChooser')
    advanced_parser_group.add_argument('--kyokus', help='Specify kyokus to review. If LIST is empty, review all kyokus. Format: "E1,E4,S3.1".')
    advanced_parser_group.add_argument('--lang', help='Set the language for the rendered report page. Default value "ja". Supported languages: ja, en.', choices=['ja', 'en'], nargs=1)
    advanced_parser_group.add_argument('--mjai-out', help='Save the transformed mjai format log to FILE. If FILE is "-", write to stdout.', widget='FileSaver')
    advanced_parser_group.add_argument('--mjsoul-id', help='Specify a Mahjong Soul log ID to review. Example: "200417-e1f9e08d-487f-4333-989f-34be08b943c7"')
    advanced_parser_group.add_argument('--out-dir', help='Specify a directory to save the output for mjai logs. If DIR is empty, defaults to ".".', widget='DirChooser')
    advanced_parser_group.add_argument('--out-file', help='Specify the output file for generated HTML report. If FILE is "-", write to stdout; if FILE is empty, write to "{tenhou_id}&tw={actor}.html" if --tenhou-id is specified, otherwise "report.html".', widget='FileSaver')
    advanced_parser_group.add_argument('--pt', help='Shortcut to override "jun_pt" in --tactics-config. Format: "90,45,0,-135".')
    advanced_parser_group.add_argument('--tactics-config', help='Specify the tactics config file for akochan. Default value "tactics.json".', default=".\\akochan-reviewer\\tactics.json", widget='FileChooser')
    advanced_parser_group.add_argument('--tenhou-id', help='Specify a Tenhou log ID to review, overriding --in-file. Example: "2019050417gm-0029-0000-4f2a8622".')
    advanced_parser_group.add_argument('--tenhou-ids-file', help='Specify a file of Tenhou log ID list to convert to mjai format, implying --no-review.', widget='FileChooser')
    advanced_parser_group.add_argument('--tenhou-out', help='Save the downloaded tenhou.net/6 format log to FILE when --tenhou-id is specified. If FILE is "-", write to stdout.', widget='FileSaver')
    advanced_parser_group.add_argument('--url', help='Tenhou or Mahjong Soul log URL.')

    args = parser.parse_args()

    # print(args, flush=True)

    command = args.akochan_reviewer
    if hasattr(args, 'anonymous') and args.anonymous:
        command += ' --anonymous'
    if hasattr(args, 'json') and args.json:
        command += ' --json'
    if hasattr(args, 'no_open') and args.no_open:
        command += ' --no-open'
    if hasattr(args, 'no_review') and args.no_review:
        command += ' --no-review'
    if hasattr(args, 'use_placement_ev') and args.use_placement_ev:
        command += ' --use-placement-ev'
    if hasattr(args, 'verbose') and args.verbose:
        command += ' --verbose'
    if hasattr(args, 'without_viewer') and args.without_viewer:
        command += ' --without-viewer'

    if hasattr(args, 'actor') and args.actor is not None:
        command += ' --actor ' + args.actor
    if hasattr(args, 'akochan_dir') and args.akochan_dir is not None:
        command += ' --akochan-dir "' + args.akochan_dir + '"'
    if hasattr(args, 'deviation_threshold') and args.deviation_threshold is not None:
        command += ' --deviation-threshold ' + args.deviation_threshold
    if hasattr(args, 'in_file') and args.in_file is not None:
        command += ' --in-file "' + args.in_file + '"'
    if hasattr(args, 'kyokus') and args.kyokus is not None:
        command += ' --kyokus ' + args.kyokus
    if hasattr(args, 'lang') and args.lang is not None and len(args.lang) > 0:
        command += ' --lang ' + args.lang[0]
    if hasattr(args, 'mjai_out') and args.mjai_out is not None:
        command += ' --mjai-out "' + args.mjai_out + '"'
    if hasattr(args, 'mjsoul_id') and args.mjsoul_id is not None:
        command += ' --mjsoul-id ' + args.mjsoul_id
    if hasattr(args, 'out_dir') and args.out_dir is not None:
        command += ' --out-dir "' + args.out_dir + '"'
    if hasattr(args, 'out_file') and args.out_file is not None:
        command += ' --out-file "' + args.out_file + '"'
    if hasattr(args, 'pt') and args.pt is not None:
        command += ' --pt ' + args.pt
    if hasattr(args, 'tactics_config') and args.tactics_config is not None:
        command += ' --tactics-config "' + args.tactics_config + '"'
    if hasattr(args, 'tenhou_id') and args.tenhou_id is not None:
        command += ' --tenhou-id ' + args.tenhou_id
    if hasattr(args, 'tenhou_ids_file') and args.tenhou_ids_file is not None:
        command += ' --tenhou-ids-file "' + args.tenhou_ids_file + '"'
    if hasattr(args, 'tenhou_out') and args.tenhou_out is not None:
        command += ' --tenhou-out "' + args.tenhou_out + '"'
    if hasattr(args, 'url') and args.url is not None:
        command += ' ' + args.url

    print(command, flush=True)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
   
    with subprocess.Popen(
        command,
        startupinfo=startupinfo,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
    ) as p:
        for line in p.stdout:
            print(line.decode('UTF-8', errors="ignore"), end='', flush=True)

if __name__ == '__main__':
    main()